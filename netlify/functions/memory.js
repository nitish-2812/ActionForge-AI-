/**
 * memory.js — Memory endpoint for ActionForge AI on Netlify.
 * Note: Serverless functions are stateless, so memory doesn't persist
 * between invocations. This returns an empty state for compatibility.
 */
exports.handler = async (event) => {
  // Handle CORS preflight
  if (event.httpMethod === "OPTIONS") {
    return {
      statusCode: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
      body: "",
    };
  }

  if (event.httpMethod === "DELETE") {
    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
      body: JSON.stringify({ status: "memory cleared" }),
    };
  }

  // GET
  return {
    statusCode: 200,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
    body: JSON.stringify({
      count: 0,
      meetings: [],
      context_preview: "No previous context",
    }),
  };
};
