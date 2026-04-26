"""
main.py — FastAPI application for ActionForge AI.
Exposes endpoints for processing meeting notes via MCP-style tool pipeline.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import io
import tempfile
import os
from openai import OpenAI
from typing import List

from models import MeetingInput, ActionPlanResponse
from memory import add_to_memory, get_memory_context, get_memory_store, clear_memory
from tools import (
    generate_summary,
    extract_tasks,
    extract_deadlines,
    assign_roles,
    generate_email,
)
from export import generate_pdf_export, generate_csv_export
from collaboration import user_manager, session_manager, User, SharedSession, Permission

# ---------------------------------------------------------------------------
# App initialization
# ---------------------------------------------------------------------------
app = FastAPI(
    title="ActionForge AI",
    description="Convert unstructured sales meeting notes into structured action plans using LLM-powered MCP-style tools.",
    version="2.0.0",
)

# CORS — allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def health_check():
    """Health check endpoint — confirms the API is running."""
    return {
        "status": "ActionForge AI running",
        "version": "2.0.0",
        "model": "llama-3.3-70b-versatile (Groq)",
    }


@app.post("/process_notes", response_model=ActionPlanResponse)
def process_notes(payload: MeetingInput):
    """
    Main pipeline endpoint.
    Receives meeting notes, runs all 5 MCP-style tools sequentially,
    saves results to memory, and returns a full action plan.
    """
    notes = payload.notes
    meeting_date = payload.meeting_date

    try:
        # Get memory context for continuity between meetings
        context = get_memory_context()
        memory_used = bool(context)

        # If a meeting date was provided, prepend it to the notes for the LLM
        if meeting_date:
            notes_with_date = f"Meeting date: {meeting_date}\n\n{notes}"
        else:
            notes_with_date = notes

        # --- MCP Tool Pipeline (sequential) ---
        # Tool 1: Generate executive summary
        summary = generate_summary(notes_with_date, context)

        # Tool 2: Extract action items
        tasks = extract_tasks(notes_with_date, context)

        # Tool 3: Extract deadlines
        deadlines = extract_deadlines(notes_with_date, context)

        # Tool 4: Assign roles
        assigned = assign_roles(notes_with_date, context)

        # Tool 5: Generate follow-up email (uses outputs from tools 2-4)
        email = generate_email(notes_with_date, tasks, deadlines, assigned, context)

        # Build the result dict
        result = {
            "summary": summary,
            "tasks": tasks,
            "deadlines": deadlines,
            "assigned": assigned,
            "email": email,
            "memory_used": memory_used,
        }

        # Save to session memory for future context
        add_to_memory(notes, result)

        return ActionPlanResponse(**result)

    except HTTPException:
        # Re-raise FastAPI HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process meeting notes: {str(e)}",
        )


@app.get("/memory")
def get_memory():
    """
    Returns the current session memory store.
    Shows what context the LLM is using for continuity.
    """
    store = get_memory_store()
    return {
        "count": len(store),
        "meetings": store,
        "context_preview": get_memory_context() or "No previous context",
    }


@app.delete("/memory")
def delete_memory():
    """Clears all stored meeting memory."""
    clear_memory()
    return {"status": "memory cleared"}


# ---------------------------------------------------------------------------
# Audio Transcription Endpoint
# ---------------------------------------------------------------------------

@app.post("/transcribe_audio")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe an audio file using OpenAI's Whisper API.
    
    Supports: MP3, MP4, MPEG, MPGA, M4A, WAV, WEBM
    
    Args:
        file: Audio file upload.
    
    Returns:
        Transcribed text extracted from the audio.
    """
    try:
        # Validate file type
        allowed_types = {
            "audio/mpeg",
            "audio/mp4",
            "audio/wav",
            "audio/webm",
            "audio/x-m4a",
            "audio/m4a",
        }
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format. Allowed: MP3, MP4, WAV, WEBM, M4A. Got: {file.content_type}"
            )
        
        # Read file content
        content = await file.read()
        
        # Create a temporary file to store audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".audio") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Initialize OpenAI client
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Open and transcribe the audio file
            with open(tmp_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"
                )
            
            return {
                "text": transcript.text,
                "filename": file.filename,
                "status": "success"
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to transcribe audio: {str(e)}"
        )


# ---------------------------------------------------------------------------
# Export Endpoints
# ---------------------------------------------------------------------------

class ExportRequest(BaseModel):
    """Request model for export endpoints."""
    data: dict
    meeting_date: str = None


@app.post("/export/pdf")
def export_pdf(request: ExportRequest):
    """
    Export the action plan as a PDF file.
    
    Args:
        request: ExportRequest containing the action plan data and meeting date.
    
    Returns:
        PDF file for download.
    """
    try:
        pdf_bytes = generate_pdf_export(request.data, request.meeting_date)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=action-plan.pdf"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF: {str(e)}"
        )


@app.post("/export/csv")
def export_csv(request: ExportRequest):
    """
    Export the action plan as a CSV file.
    
    Args:
        request: ExportRequest containing the action plan data and meeting date.
    
    Returns:
        CSV file for download.
    """
    try:
        csv_content = generate_csv_export(request.data, request.meeting_date)
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=action-plan.csv"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate CSV: {str(e)}"
        )


# ---------------------------------------------------------------------------
# Collaboration Endpoints
# ---------------------------------------------------------------------------

class UserRegistration(BaseModel):
    """User registration request."""
    email: str
    username: str
    password: str


class UserLogin(BaseModel):
    """User login request."""
    email: str
    password: str


class SessionCreate(BaseModel):
    """Create a new shared session."""
    name: str
    description: str = ""
    meeting_data: dict = {}


class SessionShare(BaseModel):
    """Share a session with another user."""
    target_email: str
    permission: str = "view"  # view, edit, admin


@app.post("/auth/register", response_model=dict)
def register_user(req: UserRegistration):
    """
    Register a new user.
    
    Args:
        req: Registration details (email, username, password).
    
    Returns:
        User object with ID.
    """
    try:
        user = user_manager.create_user(req.email, req.username, req.password)
        return {
            "status": "success",
            "user_id": user.id,
            "email": user.email,
            "username": user.username,
            "message": "User registered successfully!"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.post("/auth/login", response_model=dict)
def login_user(req: UserLogin):
    """
    Authenticate a user.
    
    Args:
        req: Login credentials (email, password).
    
    Returns:
        User object with ID if successful.
    """
    try:
        user = user_manager.authenticate(req.email, req.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        return {
            "status": "success",
            "user_id": user.id,
            "email": user.email,
            "username": user.username,
            "message": "Login successful!"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@app.post("/sessions/create", response_model=dict)
def create_session(user_id: str, req: SessionCreate):
    """
    Create a new shared session.
    
    Args:
        user_id: ID of the session owner.
        req: Session details.
    
    Returns:
        Created session object.
    """
    try:
        session = session_manager.create_session(
            owner_id=user_id,
            name=req.name,
            description=req.description,
            meeting_data=req.meeting_data
        )
        return {
            "status": "success",
            "session_id": session.id,
            "name": session.name,
            "owner_id": session.owner_id,
            "created_at": session.created_at.isoformat(),
            "message": "Session created successfully!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@app.get("/sessions/list")
def list_user_sessions(user_id: str):
    """
    Get all sessions accessible by the user.
    
    Args:
        user_id: ID of the user.
    
    Returns:
        List of accessible sessions.
    """
    try:
        sessions = session_manager.get_user_sessions(user_id)
        return {
            "status": "success",
            "count": len(sessions),
            "sessions": [
                {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description,
                    "owner_id": s.owner_id,
                    "created_at": s.created_at.isoformat(),
                    "is_owner": s.owner_id == user_id,
                    "shared_with_count": len(s.shared_with)
                }
                for s in sessions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sessions: {str(e)}")


@app.get("/sessions/{session_id}")
def get_session(session_id: str, user_id: str):
    """
    Get a specific session if user has access.
    
    Args:
        session_id: ID of the session.
        user_id: ID of the user requesting access.
    
    Returns:
        Session data if user has access.
    """
    try:
        if not session_manager.can_access(user_id, session_id, "view"):
            raise HTTPException(status_code=403, detail="You don't have access to this session")
        
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "status": "success",
            "session": {
                "id": session.id,
                "name": session.name,
                "description": session.description,
                "owner_id": session.owner_id,
                "meeting_data": session.meeting_data,
                "shared_with": session.shared_with,
                "public": session.public,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch session: {str(e)}")


@app.post("/sessions/{session_id}/share")
def share_session(session_id: str, user_id: str, req: SessionShare):
    """
    Share a session with another user.
    
    Args:
        session_id: ID of the session to share.
        user_id: ID of the session owner.
        req: Sharing details (target_email, permission level).
    
    Returns:
        Confirmation of sharing.
    """
    try:
        # Verify user is owner or admin
        if not session_manager.can_access(user_id, session_id, "admin"):
            # Check if owner
            session = session_manager.get_session(session_id)
            if not session or session.owner_id != user_id:
                raise HTTPException(status_code=403, detail="You don't have permission to share this session")
        
        # Find target user by email
        target_user = user_manager.get_user_by_email(req.target_email)
        if not target_user:
            raise HTTPException(status_code=404, detail=f"User with email '{req.target_email}' not found")
        
        # Share session
        perm = session_manager.share_session(
            session_id=session_id,
            target_user_id=target_user.id,
            permission=req.permission,
            granted_by=user_id
        )
        
        return {
            "status": "success",
            "message": f"Session shared with {req.target_email} ({req.permission} permission)",
            "shared_with": target_user.email,
            "permission": perm.permission,
            "granted_at": perm.granted_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to share session: {str(e)}")


@app.put("/sessions/{session_id}/update")
def update_session(session_id: str, user_id: str, req: dict):
    """
    Update session data (only owner can update).
    
    Args:
        session_id: ID of the session.
        user_id: ID of the user.
        req: Updated session data.
    
    Returns:
        Updated session.
    """
    try:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Only the owner can update this session")
        
        updated = session_manager.update_session(session_id, **req)
        
        return {
            "status": "success",
            "session": {
                "id": updated.id,
                "name": updated.name,
                "description": updated.description,
                "meeting_data": updated.meeting_data,
                "updated_at": updated.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")


@app.delete("/sessions/{session_id}")
def delete_session(session_id: str, user_id: str):
    """
    Delete a session (only owner can delete).
    
    Args:
        session_id: ID of the session.
        user_id: ID of the user.
    
    Returns:
        Confirmation of deletion.
    """
    try:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Only the owner can delete this session")
        
        session_manager.delete_session(session_id)
        
        return {"status": "success", "message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")
