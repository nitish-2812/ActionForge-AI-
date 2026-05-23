/**
 * export_csv.js — CSV export for ActionForge AI on Netlify.
 */
exports.handler = async (event) => {
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
    return { statusCode: 405, body: "Method not allowed" };
  }

  try {
    const { data, meeting_date } = JSON.parse(event.body);
    const now = new Date().toISOString().replace("T", " ").slice(0, 19);

    let csv = "";
    csv += `"ActionForge AI — Action Plan Export"\n`;
    csv += `"Generated: ${now}"\n`;
    if (meeting_date) csv += `"Meeting Date: ${meeting_date}"\n`;
    csv += `\n`;

    // Summary
    csv += `"MEETING SUMMARY"\n`;
    csv += `"${(data.summary || "").replace(/"/g, '""')}"\n\n`;

    // Tasks
    csv += `"ACTION ITEMS"\n`;
    csv += `"#","Task","Priority","Owner"\n`;
    const tasks = data.tasks || [];
    const assigned = data.assigned || [];
    tasks.forEach((task, i) => {
      let owner = "Team";
      for (const a of assigned) {
        if (a.task && task.task) {
          if (a.task.toLowerCase().includes(task.task.toLowerCase()) ||
              task.task.toLowerCase().includes(a.task.toLowerCase())) {
            owner = a.person;
            break;
          }
        }
      }
      csv += `"${i + 1}","${(task.task || "").replace(/"/g, '""')}","${task.priority || ""}","${owner}"\n`;
    });
    csv += `\n`;

    // Deadlines
    csv += `"DEADLINES"\n`;
    csv += `"Item","Deadline","Urgency"\n`;
    (data.deadlines || []).forEach((d) => {
      csv += `"${(d.item || "").replace(/"/g, '""')}","${d.deadline || ""}","${d.urgency || ""}"\n`;
    });
    csv += `\n`;

    // Assignments
    csv += `"ROLE ASSIGNMENTS"\n`;
    csv += `"Person","Responsibility","Task"\n`;
    (data.assigned || []).forEach((a) => {
      csv += `"${a.person || ""}","${(a.responsibility || "").replace(/"/g, '""')}","${(a.task || "").replace(/"/g, '""')}"\n`;
    });
    csv += `\n`;

    // Email
    csv += `"FOLLOW-UP EMAIL"\n`;
    csv += `"${(data.email || "").replace(/"/g, '""')}"\n`;

    return {
      statusCode: 200,
      headers: {
        "Content-Type": "text/csv",
        "Content-Disposition": "attachment; filename=action-plan.csv",
        "Access-Control-Allow-Origin": "*",
      },
      body: csv,
    };
  } catch (e) {
    return {
      statusCode: 500,
      headers: { "Access-Control-Allow-Origin": "*" },
      body: JSON.stringify({ error: `Failed to generate CSV: ${e.message}` }),
    };
  }
};
