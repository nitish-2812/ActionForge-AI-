"""
tools.py — MCP-style tool functions for ActionForge AI.
Each tool calls the LLM independently with a focused prompt.
One tool, one job — mirrors real MCP and AI agent systems.
"""

import json
import re
from typing import List, Dict, Any

from llm import call_llm
from prompts import (
    TASK_EXTRACTOR_PROMPT,
    DEADLINE_EXTRACTOR_PROMPT,
    ROLE_ASSIGNER_PROMPT,
    EMAIL_WRITER_PROMPT,
    SUMMARY_WRITER_PROMPT,
)


def _parse_json_response(raw: str) -> Any:
    """
    Safely parse a JSON response from the LLM.
    Handles cases where the LLM wraps JSON in markdown code fences.

    Args:
        raw: The raw string response from the LLM.

    Returns:
        Parsed JSON (list or dict), or None on failure.
    """
    # Strip markdown code fences if present
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find a JSON array in the response
        match = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return None


def extract_tasks(notes: str, context: str) -> List[Dict[str, str]]:
    """
    TOOL 1: Extract action items from meeting notes.

    Args:
        notes: Raw meeting notes text.
        context: Previous meeting context from memory.

    Returns:
        List of dicts with 'task' and 'priority' keys.
    """
    prompt = f"""Previous context: {context}

Meeting notes: {notes}

Extract all action items as a JSON array:
[
  {{
    "task": "action description",
    "priority": "High | Medium | Low"
  }}
]
Return ONLY the JSON array. No explanation."""

    try:
        raw = call_llm(prompt=prompt, system=TASK_EXTRACTOR_PROMPT)
        parsed = _parse_json_response(raw)
        if isinstance(parsed, list):
            # Validate each item has required keys
            return [
                {"task": item.get("task", ""), "priority": item.get("priority", "Medium")}
                for item in parsed
                if item.get("task")
            ]
    except Exception as e:
        print(f"[ActionForge] extract_tasks failed: {e}")

    return []


def extract_deadlines(notes: str, context: str) -> List[Dict[str, str]]:
    """
    TOOL 2: Extract deadlines and timeframes from meeting notes.

    Args:
        notes: Raw meeting notes text.
        context: Previous meeting context from memory.

    Returns:
        List of dicts with 'item', 'deadline', and 'urgency' keys.
    """
    prompt = f"""Previous context: {context}

Meeting notes: {notes}

Extract all deadlines as a JSON array:
[
  {{
    "item": "what is due",
    "deadline": "specific date or timeframe",
    "urgency": "Immediate | Soon | Flexible"
  }}
]
Return ONLY the JSON array. No explanation."""

    try:
        raw = call_llm(prompt=prompt, system=DEADLINE_EXTRACTOR_PROMPT)
        parsed = _parse_json_response(raw)
        if isinstance(parsed, list):
            return [
                {
                    "item": item.get("item", ""),
                    "deadline": item.get("deadline", "TBD"),
                    "urgency": item.get("urgency", "Flexible"),
                }
                for item in parsed
                if item.get("item")
            ]
    except Exception as e:
        print(f"[ActionForge] extract_deadlines failed: {e}")

    return []


def assign_roles(notes: str, context: str) -> List[Dict[str, str]]:
    """
    TOOL 3: Identify people and their task assignments from meeting notes.

    Args:
        notes: Raw meeting notes text.
        context: Previous meeting context from memory.

    Returns:
        List of dicts with 'person', 'responsibility', and 'task' keys.
    """
    prompt = f"""Previous context: {context}

Meeting notes: {notes}

Extract all role assignments as a JSON array. For each task mentioned, identify the person assigned:
[
  {{
    "person": "exact name of person or 'Unassigned'",
    "responsibility": "area of ownership/domain",
    "task": "specific task they must complete"
  }}
]
Return ONLY the JSON array. Include all tasks even if person is 'Unassigned'. No explanation."""

    try:
        raw = call_llm(prompt=prompt, system=ROLE_ASSIGNER_PROMPT)
        parsed = _parse_json_response(raw)
        if isinstance(parsed, list):
            # Include all entries, even with "Unassigned"
            result = []
            for item in parsed:
                person = item.get("person", "").strip() or "Unassigned"
                responsibility = item.get("responsibility", "").strip()
                task = item.get("task", "").strip()
                if task:  # Only include if task is not empty
                    result.append({
                        "person": person,
                        "responsibility": responsibility,
                        "task": task,
                    })
            return result
    except Exception as e:
        print(f"[ActionForge] assign_roles failed: {e}")

    return []


def generate_email(
    notes: str,
    tasks: List[Dict[str, str]],
    deadlines: List[Dict[str, str]],
    assigned: List[Dict[str, str]],
    context: str,
) -> str:
    """
    TOOL 4: Generate a professional follow-up email from processed meeting data.

    Args:
        notes: Raw meeting notes text.
        tasks: Extracted action items list.
        deadlines: Extracted deadlines list.
        assigned: Extracted role assignments list.
        context: Previous meeting context from memory.

    Returns:
        Complete follow-up email as a string.
    """
    prompt = f"""Previous context: {context}

Meeting notes: {notes}
Extracted tasks: {json.dumps(tasks)}
Deadlines: {json.dumps(deadlines)}
Assignments: {json.dumps(assigned)}

Write a professional follow-up email that:
- Has a clear subject line on the first line
- Summarizes the meeting in 2 sentences
- Lists all action items with owners and deadlines
- Has a professional closing

Return ONLY the email text. No explanation."""

    try:
        return call_llm(prompt=prompt, system=EMAIL_WRITER_PROMPT)
    except Exception as e:
        print(f"[ActionForge] generate_email failed: {e}")

    return ""


def generate_summary(notes: str, context: str) -> str:
    """
    TOOL 5: Generate a concise executive summary of the meeting.

    Args:
        notes: Raw meeting notes text.
        context: Previous meeting context from memory.

    Returns:
        2-3 sentence executive summary string.
    """
    prompt = f"""Previous context: {context}

Meeting notes: {notes}

Write a 2-3 sentence executive summary of this meeting.
Focus on decisions made and outcomes.
Return ONLY the summary text."""

    try:
        return call_llm(prompt=prompt, system=SUMMARY_WRITER_PROMPT)
    except Exception as e:
        print(f"[ActionForge] generate_summary failed: {e}")

    return ""
