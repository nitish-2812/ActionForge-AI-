"""
memory.py — In-memory session store for ActionForge AI.
Stores last 5 meetings and provides context injection for LLM prompts.
"""

from datetime import datetime
from typing import List, Dict, Any

# Global in-memory store — holds up to 5 recent meetings
meeting_memory: List[Dict[str, Any]] = []

# Maximum number of meetings to keep in memory
MAX_MEMORY_SIZE = 5

# Number of recent meetings to inject as context
CONTEXT_WINDOW = 2


def add_to_memory(notes: str, result: dict) -> None:
    """
    Store a processed meeting in memory.
    Trims older entries to keep only the last MAX_MEMORY_SIZE meetings.

    Args:
        notes: The original meeting notes text.
        result: The full action plan result dict.
    """
    global meeting_memory

    entry = {
        "notes": notes[:500],  # Store truncated notes to save memory
        "summary": result.get("summary", ""),
        "task_count": len(result.get("tasks", [])),
        "timestamp": datetime.now().isoformat(),
        "data": result,  # Store full result for analytics dashboard
    }

    meeting_memory.append(entry)

    # Keep only the last MAX_MEMORY_SIZE entries
    if len(meeting_memory) > MAX_MEMORY_SIZE:
        meeting_memory = meeting_memory[-MAX_MEMORY_SIZE:]


def get_memory_context() -> str:
    """
    Build a context string from the last CONTEXT_WINDOW meetings.
    This string is injected into every new LLM prompt so the model
    is aware of what was discussed in previous meetings.

    Returns:
        A formatted string with summaries of recent meetings,
        or an empty string if no meetings are stored.
    """
    if not meeting_memory:
        return ""

    # Take the last CONTEXT_WINDOW entries
    recent = meeting_memory[-CONTEXT_WINDOW:]

    context_parts = []
    for entry in recent:
        ts = entry.get("timestamp", "unknown")
        summary = entry.get("summary", "No summary available")
        task_count = entry.get("task_count", 0)
        context_parts.append(
            f"Previous meeting [{ts}]: {summary} ({task_count} action items identified)"
        )

    return "\n".join(context_parts)


def get_memory_store() -> List[Dict[str, Any]]:
    """
    Return the full memory store for the /memory endpoint.

    Returns:
        List of all stored meeting entries.
    """
    return meeting_memory


def clear_memory() -> None:
    """
    Clear all stored meetings. Used by the DELETE /memory endpoint.
    """
    global meeting_memory
    meeting_memory = []
