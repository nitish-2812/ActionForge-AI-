"""
models.py — Pydantic v2 request/response models for ActionForge AI.
Validates all input and shapes all output for the API.
"""

from typing import List
from pydantic import BaseModel, field_validator


class MeetingInput(BaseModel):
    """Request model for incoming meeting notes."""
    notes: str
    meeting_date: str = ""

    @field_validator("notes")
    @classmethod
    def must_have_content(cls, v: str) -> str:
        """Ensure notes contain meaningful content (at least 20 chars)."""
        if len(v.strip()) < 20:
            raise ValueError("Meeting notes are too short. Please provide at least 20 characters.")
        return v.strip()


class Task(BaseModel):
    """A single extracted action item."""
    task: str
    priority: str  # High | Medium | Low


class Deadline(BaseModel):
    """A single extracted deadline."""
    item: str
    deadline: str
    urgency: str  # Immediate | Soon | Flexible


class Assignment(BaseModel):
    """A single role/task assignment."""
    person: str
    responsibility: str
    task: str


class ActionPlanResponse(BaseModel):
    """Full response model returned by /process_notes."""
    summary: str
    tasks: List[Task]
    deadlines: List[Deadline]
    assigned: List[Assignment]
    email: str
    memory_used: bool
