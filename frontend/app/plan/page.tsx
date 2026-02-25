"use client";

import Link from "next/link";
import { useState } from "react";
import PlanResultView from "@/components/PlanResultView";

/** Returns the base URL for API calls. In the browser uses current origin so fetch hits Next.js API routes. */
function getApiUrl(path: string): string {
  if (typeof window !== "undefined") {
    return `${window.location.origin}${path.startsWith("/") ? path : `/${path}`}`;
  }
  return path.startsWith("/") ? `http://localhost:3000${path}` : `http://localhost:3000/${path}`;
}

type PlanState = {
  thread_id?: string;
  status: "complete" | "awaiting_approval";
  state?: Record<string, unknown>;
  interrupt?: unknown[];
};

/**
 * Plan page: trip request input, submit button, and formatted plan result / approval flow.
 */
export default function PlanPage() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PlanState | null>(null);

  async function handleSubmit() {
    const trimmed = input.trim();
    if (!trimmed) {
      setError("Please describe your trip.");
      return;
    }
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const url = getApiUrl("/api/plan");
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: trimmed }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Request failed: ${res.status}`);
      }
      const data = (await res.json()) as PlanState & { message?: string };
      if (data.message) {
        setResult({
          thread_id: data.thread_id,
          status: "complete",
          state: { message: data.message },
        });
        return;
      }
      setResult({
        thread_id: data.thread_id,
        status: data.status,
        state: data.state as Record<string, unknown>,
        interrupt: data.interrupt,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  async function handleApprove() {
    const threadId = result?.thread_id;
    if (!threadId || result?.status !== "awaiting_approval") return;
    setError(null);
    setLoading(true);
    try {
      const url = getApiUrl(`/api/plan/${threadId}/approve`);
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume: true }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Request failed: ${res.status}`);
      }
      const data = (await res.json()) as PlanState;
      setResult({
        thread_id: data.thread_id,
        status: data.status,
        state: data.state as Record<string, unknown>,
        interrupt: data.interrupt,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="plan_page">
      <nav className="plan_nav">
        <Link href="/" className="plan_back">
          ← Home
        </Link>
      </nav>
      <h1 className="plan_title">Plan your trip</h1>
      <p className="plan_subtitle">
        Describe your trip (e.g. &quot;4-day solo backpacking to Rishikesh under
        ₹15,000 from Delhi&quot;).
      </p>
      <form
        className="plan_input_wrap"
        onSubmit={(e) => {
          e.preventDefault();
          handleSubmit();
        }}
      >
        <textarea
          className="plan_input"
          placeholder="Where do you want to go? Budget, dates, interests..."
          rows={4}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          aria-label="Trip description"
        />
        <button
          type="submit"
          className="plan_submit"
          disabled={loading}
          aria-label="Create plan"
        >
          {loading ? "Planning…" : "Create plan"}
        </button>
      </form>
      {error && <p className="plan_error">{error}</p>}
      {result && (
        <div className="plan_result_container">
          <PlanResultView
            status={result.status}
            state={result.state}
            interrupt={result.interrupt}
            onApprove={handleApprove}
            approving={loading}
          />
        </div>
      )}
    </main>
  );
}
