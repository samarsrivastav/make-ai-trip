/**
 * Proxies POST /api/plan/:threadId/approve to the Python backend (resume after approval).
 */
export async function POST(
  request: Request,
  context: { params: { threadId: string } }
) {
  const { threadId } = context.params;
  const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
  const url = `${backendUrl}/api/plan/${threadId}/approve`;

  try {
    const body = await request.json();
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    return Response.json(data, { status: res.status });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Backend unreachable";
    return Response.json(
      { error: message, detail: "Ensure the Python backend is running on " + backendUrl },
      { status: 502 }
    );
  }
}
