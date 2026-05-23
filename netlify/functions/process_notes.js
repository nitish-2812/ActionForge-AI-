/**
 * process_notes.js — Netlify serverless function for ActionForge AI.
 * Replicates the full MCP-style tool pipeline from the Python backend.
 */

const Groq = require("groq-sdk");

// ── Prompts (mirrored from prompts.py) ──

const SUMMARY_WRITER_PROMPT =
  "You are a meeting summarization specialist. " +
  "Write concise executive summaries focusing on decisions made and outcomes. " +
  "Return only the summary text. No markdown, no explanation.";

const TASK_EXTRACTOR_PROMPT =
  "You are a task extraction specialist. " +
  "Extract only action items from meeting notes. " +
  "Return a valid JSON array only. No markdown, no explanation.";

const DEADLINE_EXTRACTOR_PROMPT =
  "You are a deadline extraction specialist. " +
  "Extract dates, timeframes, and due dates only. " +
  "Always convert relative time expressions to actual calendar dates " +
  "using the provided meeting_date as the anchor point. " +
  "Use these conversions: " +
  "ASAP = meeting_date + 1 business day, " +
  "EOD = meeting_date (same day), " +
  "EOW or end of week = nearest Friday from meeting_date, " +
  "Next Tuesday = nearest Tuesday from meeting_date, " +
  "Next Monday = nearest Monday from meeting_date, " +
  "Next week = meeting_date + 7 days, " +
  "Before Friday = that Friday's actual date, " +
  "No urgency mentioned = meeting_date + 5 business days. " +
  "Always return dates in this format: Apr 22, 2026. " +
  "Never return relative terms like ASAP, EOW, next week. " +
  "Return a valid JSON array only. No markdown, no explanation.";

const ROLE_ASSIGNER_PROMPT =
  "You are a role assignment specialist. " +
  "Extract all people mentioned in meeting notes and their assigned tasks/responsibilities. " +
  "For each task, identify: " +
  "1. The person's name (extract from 'X needs to...', 'X will...', 'X to...', 'X should...', 'from X' patterns) " +
  "2. Their responsibility/area (domain or topic they own) " +
  "3. The specific task assigned to them. " +
  "If no person is mentioned for a task, use 'Unassigned' as the person name. " +
  "Do NOT return entries with empty person fields. " +
  "Return a valid JSON array only. No markdown, no explanation.";

const EMAIL_WRITER_PROMPT =
  "You are a professional email writer. " +
  "Write clear, concise follow-up emails only. " +
  "End every email with exactly: Best regards, followed by " +
  "ActionForge AI Team on a new line. " +
  "Never use placeholders like [Your Name], [Name], [Your Designation] " +
  "or any bracketed placeholder text. " +
  "Always sign off as ActionForge AI Team. " +
  "Return only the email text. No markdown, no explanation.";

// ── Models ──
const PRIMARY_MODEL = "llama-3.3-70b-versatile";
const FALLBACK_MODEL = "llama-3.1-8b-instant";

// ── Helpers ──

function parseJsonResponse(raw) {
  let cleaned = raw.trim();
  cleaned = cleaned.replace(/^```(?:json)?\s*/i, "");
  cleaned = cleaned.replace(/\s*```$/i, "");
  cleaned = cleaned.trim();

  try {
    return JSON.parse(cleaned);
  } catch {
    const match = cleaned.match(/\[[\s\S]*\]/);
    if (match) {
      try {
        return JSON.parse(match[0]);
      } catch {
        return null;
      }
    }
    return null;
  }
}

async function callLLM(client, prompt, system, temperature = 0.3, maxTokens = 2048) {
  const messages = [
    { role: "system", content: system },
    { role: "user", content: prompt },
  ];

  for (const model of [PRIMARY_MODEL, FALLBACK_MODEL]) {
    try {
      const response = await client.chat.completions.create({
        model,
        messages,
        temperature,
        max_tokens: maxTokens,
      });
      const content = response.choices[0]?.message?.content;
      if (content) return content.trim();
    } catch (e) {
      if (model === PRIMARY_MODEL) {
        console.log(`Primary model failed: ${e.message}. Trying fallback...`);
        continue;
      }
      throw new Error(`Both models failed. Error: ${e.message}`);
    }
  }
  throw new Error("LLM returned empty response from both models.");
}

// ── Tool Functions ──

async function generateSummary(client, notes, context) {
  const prompt = `Previous context: ${context}\n\nMeeting notes: ${notes}\n\nWrite a 2-3 sentence executive summary of this meeting.\nFocus on decisions made and outcomes.\nReturn ONLY the summary text.`;
  try {
    return await callLLM(client, prompt, SUMMARY_WRITER_PROMPT);
  } catch (e) {
    console.error("generate_summary failed:", e.message);
    return "";
  }
}

async function extractTasks(client, notes, context) {
  const prompt = `Previous context: ${context}\n\nMeeting notes: ${notes}\n\nExtract all action items as a JSON array:\n[\n  {\n    "task": "action description",\n    "priority": "High | Medium | Low"\n  }\n]\nReturn ONLY the JSON array. No explanation.`;
  try {
    const raw = await callLLM(client, prompt, TASK_EXTRACTOR_PROMPT);
    const parsed = parseJsonResponse(raw);
    if (Array.isArray(parsed)) {
      return parsed
        .filter((item) => item.task)
        .map((item) => ({
          task: item.task || "",
          priority: item.priority || "Medium",
        }));
    }
  } catch (e) {
    console.error("extract_tasks failed:", e.message);
  }
  return [];
}

async function extractDeadlines(client, notes, context) {
  const prompt = `Previous context: ${context}\n\nMeeting notes: ${notes}\n\nExtract all deadlines as a JSON array:\n[\n  {\n    "item": "what is due",\n    "deadline": "specific date or timeframe",\n    "urgency": "Immediate | Soon | Flexible"\n  }\n]\nReturn ONLY the JSON array. No explanation.`;
  try {
    const raw = await callLLM(client, prompt, DEADLINE_EXTRACTOR_PROMPT);
    const parsed = parseJsonResponse(raw);
    if (Array.isArray(parsed)) {
      return parsed
        .filter((item) => item.item)
        .map((item) => ({
          item: item.item || "",
          deadline: item.deadline || "TBD",
          urgency: item.urgency || "Flexible",
        }));
    }
  } catch (e) {
    console.error("extract_deadlines failed:", e.message);
  }
  return [];
}

async function assignRoles(client, notes, context) {
  const prompt = `Previous context: ${context}\n\nMeeting notes: ${notes}\n\nExtract all role assignments as a JSON array. For each task mentioned, identify the person assigned:\n[\n  {\n    "person": "exact name of person or 'Unassigned'",\n    "responsibility": "area of ownership/domain",\n    "task": "specific task they must complete"\n  }\n]\nReturn ONLY the JSON array. Include all tasks even if person is 'Unassigned'. No explanation.`;
  try {
    const raw = await callLLM(client, prompt, ROLE_ASSIGNER_PROMPT);
    const parsed = parseJsonResponse(raw);
    if (Array.isArray(parsed)) {
      return parsed
        .filter((item) => (item.task || "").trim())
        .map((item) => ({
          person: (item.person || "").trim() || "Unassigned",
          responsibility: (item.responsibility || "").trim(),
          task: (item.task || "").trim(),
        }));
    }
  } catch (e) {
    console.error("assign_roles failed:", e.message);
  }
  return [];
}

async function generateEmail(client, notes, tasks, deadlines, assigned, context) {
  const prompt = `Previous context: ${context}\n\nMeeting notes: ${notes}\nExtracted tasks: ${JSON.stringify(tasks)}\nDeadlines: ${JSON.stringify(deadlines)}\nAssignments: ${JSON.stringify(assigned)}\n\nWrite a professional follow-up email that:\n- Has a clear subject line on the first line\n- Summarizes the meeting in 2 sentences\n- Lists all action items with owners and deadlines\n- Has a professional closing\n\nReturn ONLY the email text. No explanation.`;
  try {
    return await callLLM(client, prompt, EMAIL_WRITER_PROMPT);
  } catch (e) {
    console.error("generate_email failed:", e.message);
    return "";
  }
}

// ── Main Handler ──

exports.handler = async (event) => {
  // Handle CORS preflight
  if (event.httpMethod === "OPTIONS") {
    return {
      statusCode: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
      body: "",
    };
  }

  if (event.httpMethod !== "POST") {
    return {
      statusCode: 405,
      headers: { "Access-Control-Allow-Origin": "*" },
      body: JSON.stringify({ error: "Method not allowed" }),
    };
  }

  try {
    const { notes, meeting_date } = JSON.parse(event.body);

    if (!notes || notes.trim().length < 20) {
      return {
        statusCode: 400,
        headers: { "Access-Control-Allow-Origin": "*" },
        body: JSON.stringify({
          error: "Meeting notes are too short. Please provide at least 20 characters.",
        }),
      };
    }

    // Initialize Groq client
    const apiKey = process.env.GROQ_API_KEY;
    if (!apiKey) {
      return {
        statusCode: 500,
        headers: { "Access-Control-Allow-Origin": "*" },
        body: JSON.stringify({ error: "GROQ_API_KEY not configured." }),
      };
    }

    const client = new Groq({ apiKey });

    // Prepare notes with date context
    const notesWithDate = meeting_date
      ? `Meeting date: ${meeting_date}\n\n${notes}`
      : notes;

    const context = ""; // Serverless = no persistent memory

    // Run all 5 tools sequentially (same as Python pipeline)
    const summary = await generateSummary(client, notesWithDate, context);
    const tasks = await extractTasks(client, notesWithDate, context);
    const deadlines = await extractDeadlines(client, notesWithDate, context);
    const assigned = await assignRoles(client, notesWithDate, context);
    const email = await generateEmail(client, notesWithDate, tasks, deadlines, assigned, context);

    const result = {
      summary,
      tasks,
      deadlines,
      assigned,
      email,
      memory_used: false,
    };

    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
      body: JSON.stringify(result),
    };
  } catch (e) {
    console.error("process_notes error:", e);
    return {
      statusCode: 500,
      headers: { "Access-Control-Allow-Origin": "*" },
      body: JSON.stringify({
        error: `Failed to process meeting notes: ${e.message}`,
      }),
    };
  }
};
