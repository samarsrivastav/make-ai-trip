/**
 * Proxies POST /api/plan to the Python backend (create plan).
 */
export async function POST(request: Request) {
  const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
  const url = `${backendUrl}/api/plan`;

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
