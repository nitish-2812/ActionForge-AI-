/**
 * health.js — Health check endpoint for ActionForge AI on Netlify.
 */
exports.handler = async (event) => {
  return {
    statusCode: 200,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
    body: JSON.stringify({
      status: "ActionForge AI running",
      version: "2.0.0",
      model: "llama-3.3-70b-versatile (Groq)",
      platform: "Netlify Functions",
    }),
  };
};
