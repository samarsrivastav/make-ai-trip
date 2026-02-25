/**
 * Home page: trip planning input and entry point.
 */
export default function HomePage() {
  return (
    <main className="home">
      <h1 className="home_title">AI Travel Planning &amp; Booking</h1>
      <p className="home_subtitle">
        Plan your trip with multi-agent workflow and human-in-the-loop approvals.
      </p>
      <a href="/plan" className="home_cta">
        Start planning
      </a>
    </main>
  );
}
