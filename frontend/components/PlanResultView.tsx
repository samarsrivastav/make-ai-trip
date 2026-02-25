"use client";

import React, { type ReactNode } from "react";

/** Parsed intent from backend */
type ParsedIntent = {
  budget_total?: number;
  currency?: string;
  origin?: string;
  destination?: string;
  num_days?: number;
  travel_style?: string;
  interests?: string[];
};

/** Flight / hotel / activity / weather items from backend */
type FlightOption = {
  origin: string;
  destination: string;
  departure?: string;
  arrival?: string;
  carrier?: string;
  price?: number;
  currency?: string;
  booking_link?: string;
};

type HotelOption = {
  name: string;
  address?: string;
  price_per_night?: number;
  currency?: string;
  rating?: number;
  booking_link?: string;
  map_link?: string;
};

type ActivityOption = {
  name: string;
  type?: string;
  duration_minutes?: number;
  price?: number;
  currency?: string;
  booking_link?: string;
  map_link?: string;
};

type WeatherInfo = {
  location: string;
  date: string;
  summary?: string;
  temp_min?: number;
  temp_max?: number;
  conditions?: string;
};

type BudgetAllocation = {
  transport?: number;
  stay?: number;
  food?: number;
  activities?: number;
  buffer?: number;
  currency?: string;
  reasoning?: string;
};

type DayItem = {
  time?: string;
  title: string;
  duration_minutes?: number;
  description?: string;
  price?: number;
  currency?: string;
  map_link?: string;
  booking_link?: string;
};

type DayPlan = {
  day: number;
  date?: string;
  items?: DayItem[];
  travel_notes?: string;
};

type BookingOption = {
  type: string;
  label: string;
  details?: Record<string, unknown>;
  booking_link?: string;
  map_link?: string;
  contact?: string;
  price?: number;
  currency?: string;
};

type DecisionLogEntry = {
  agent?: string;
  step?: string;
  message?: string;
};

type ResearchedData = {
  flights?: FlightOption[];
  hotels?: HotelOption[];
  activities?: ActivityOption[];
  weather?: WeatherInfo[];
  local_tips?: string[];
};

type PlanState = {
  parsed_intent?: ParsedIntent;
  destination_shortlist?: string[];
  researched_data?: ResearchedData;
  budget_allocation?: BudgetAllocation;
  approved_budget?: BudgetAllocation;
  day_by_day_itinerary?: DayPlan[];
  booking_options?: BookingOption[];
  decision_log?: DecisionLogEntry[];
};

/** Payload shape when the graph is at an approval checkpoint */
type InterruptPayload = {
  message?: string;
  checkpoint?: string;
  destination_shortlist?: string[];
  budget_allocation?: BudgetAllocation;
  day_by_day_itinerary?: DayPlan[];
};

type PlanResultViewProps = {
  status: "complete" | "awaiting_approval";
  state?: PlanState | Record<string, unknown>;
  interrupt?: unknown[];
  onApprove?: () => void;
  approving?: boolean;
};

function Section({
  title,
  icon,
  children,
}: {
  title: string;
  icon: string;
  children: ReactNode;
}) {
  return (
    <section className="result_section">
      <h3 className="result_section_title">
        <span className="result_section_icon" aria-hidden="true">{icon}</span>
        {title}
      </h3>
      {children}
    </section>
  );
}

function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`result_card ${className}`.trim()}>{children}</div>;
}

function ResultWrapper({ children }: { children: ReactNode }) {
  return <div className="result_wrapper">{children}</div>;
}

function formatMoney(amount: number, currency = "INR") {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(amount);
}

type PlanResultContentProps = {
  intent: ParsedIntent | undefined;
  shortlist: string[];
  researched: ResearchedData | undefined;
  budget: BudgetAllocation | undefined;
  itinerary: DayPlan[];
  bookings: BookingOption[];
  decisionLog: DecisionLogEntry[];
  state: PlanState | Record<string, unknown>;
};

/**
 * Renders the full plan result: trip summary, flights, hotels, activities, budget, itinerary, bookings, reasoning.
 */
function PlanResultContent({
  intent,
  shortlist,
  researched,
  budget,
  itinerary,
  bookings,
  decisionLog,
  state,
}: PlanResultContentProps) {
  return (
    <ResultWrapper>
      {intent ? (
        <Section title="Trip summary" icon="✈️">
          <Card>
            <div className="result_summary_grid">
              {intent.destination && (
                <div className="result_summary_item">
                  <span className="result_summary_label">Destination</span>
                  <span className="result_summary_value">{intent.destination}</span>
                </div>
              )}
              {intent.origin && (
                <div className="result_summary_item">
                  <span className="result_summary_label">From</span>
                  <span className="result_summary_value">{intent.origin}</span>
                </div>
              )}
              {intent.num_days != null && (
                <div className="result_summary_item">
                  <span className="result_summary_label">Days</span>
                  <span className="result_summary_value">{intent.num_days}</span>
                </div>
              )}
              {intent.budget_total != null && (
                <div className="result_summary_item">
                  <span className="result_summary_label">Budget</span>
                  <span className="result_summary_value">{formatMoney(intent.budget_total, intent.currency)}</span>
                </div>
              )}
              {intent.travel_style && (
                <div className="result_summary_item">
                  <span className="result_summary_label">Style</span>
                  <span className="result_summary_value">{intent.travel_style.replace(/_/g, " ")}</span>
                </div>
              )}
            </div>
            {intent.interests?.length ? (
              <div className="result_interests">
                {intent.interests.map((i) => (
                  <span key={i} className="result_pill result_pill_interest">{i}</span>
                ))}
              </div>
            ) : null}
          </Card>
        </Section>
      ) : null}

      {shortlist.length > 0 && !intent ? (
        <Section title="Destinations" icon="📍">
          <div className="result_pills">
            {shortlist.map((d) => (
              <span key={d} className="result_pill">{d}</span>
            ))}
          </div>
        </Section>
      ) : null}

      {researched?.flights?.length ? (
        <Section title="Flights" icon="🛫">
          <div className="result_cards">
            {researched.flights.map((f, i) => (
              <Card key={i}>
                <div className="result_flight">
                  <span className="result_flight_route">{f.origin} → {f.destination}</span>
                  {(f.departure || f.arrival) && (
                    <span className="result_flight_time">{[f.departure, f.arrival].filter(Boolean).join(" · ")}</span>
                  )}
                  {f.carrier && <span className="result_flight_carrier">{f.carrier}</span>}
                  <div className="result_flight_footer">
                    {f.price != null && <span className="result_price">{formatMoney(f.price, f.currency)}</span>}
                    {f.booking_link && (
                      <a href={f.booking_link} target="_blank" rel="noopener noreferrer" className="result_link_btn">
                        Book
                      </a>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </Section>
      ) : null}

      {researched?.hotels?.length ? (
        <Section title="Stay" icon="🏨">
          <div className="result_cards">
            {researched.hotels.map((h, i) => (
              <Card key={i}>
                <div className="result_hotel">
                  <span className="result_hotel_name">{h.name}</span>
                  {h.address && <span className="result_hotel_address">{h.address}</span>}
                  <div className="result_hotel_footer">
                    {h.price_per_night != null && <span className="result_price">{formatMoney(h.price_per_night, h.currency)}/night</span>}
                    {h.rating != null && <span className="result_rating">★ {h.rating}</span>}
                    <span className="result_link_group">
                      {h.booking_link && <a href={h.booking_link} target="_blank" rel="noopener noreferrer" className="result_link_btn">Book</a>}
                      {h.map_link && <a href={h.map_link} target="_blank" rel="noopener noreferrer" className="result_link_btn result_link_btn_secondary">Map</a>}
                    </span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </Section>
      ) : null}

      {researched?.activities?.length ? (
        <Section title="Activities" icon="🎯">
          <div className="result_cards result_cards_compact">
            {researched.activities.map((a, i) => (
              <Card key={i}>
                <div className="result_activity">
                  <span className="result_activity_name">{a.name}</span>
                  {(a.type || a.duration_minutes) && (
                    <span className="result_activity_meta">
                      {[a.type, a.duration_minutes ? `${a.duration_minutes} min` : null].filter(Boolean).join(" · ")}
                    </span>
                  )}
                  <div className="result_activity_footer">
                    {a.price != null && a.price > 0 && <span className="result_price">{formatMoney(a.price, a.currency)}</span>}
                    <span className="result_link_group">
                      {a.booking_link && <a href={a.booking_link} target="_blank" rel="noopener noreferrer" className="result_link_btn">Book</a>}
                      {a.map_link && <a href={a.map_link} target="_blank" rel="noopener noreferrer" className="result_link_btn result_link_btn_secondary">Map</a>}
                    </span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </Section>
      ) : null}

      {researched?.weather?.length ? (
        <Section title="Weather" icon="🌤️">
          <div className="result_weather_grid">
            {researched.weather.slice(0, 5).map((w, i) => (
              <Card key={i} className="result_weather_card">
                <span className="result_weather_date">{w.date}</span>
                <span className="result_weather_summary">{w.summary || w.conditions}</span>
                {(w.temp_min != null || w.temp_max != null) && (
                  <span className="result_weather_temp">
                    {[w.temp_min, w.temp_max].filter((t) => t != null).join("–")}°C
                  </span>
                )}
              </Card>
            ))}
          </div>
        </Section>
      ) : null}

      {researched?.local_tips?.length ? (
        <Section title="Local tips" icon="💡">
          <ul className="result_tips">
            {researched.local_tips.map((tip, i) => (
              <li key={i} className="result_tip">{tip}</li>
            ))}
          </ul>
        </Section>
      ) : null}

      {budget && (budget.transport || budget.stay || budget.food || budget.activities) ? (
        <Section title="Budget breakdown" icon="💰">
          <Card>
            {budget.reasoning && <p className="result_budget_reasoning">{budget.reasoning}</p>}
            <ul className="result_budget_list result_budget_list_large">
              {(["transport", "stay", "food", "activities", "buffer"] as const).map((key) => {
                const val = budget[key];
                if (val == null || val === 0) return null;
                return (
                  <li key={key} className="result_budget_row">
                    <span className="result_budget_label">{key}</span>
                    <span className="result_budget_value">{formatMoney(val, budget.currency)}</span>
                  </li>
                );
              })}
            </ul>
          </Card>
        </Section>
      ) : null}

      {itinerary.length > 0 ? (
        <Section title="Day-by-day itinerary" icon="📅">
          <div className="result_itinerary">
            {itinerary.map((day) => (
              <Card key={day.day} className="result_day_card">
                <h4 className="result_day_title">Day {day.day}{day.date ? ` · ${day.date}` : ""}</h4>
                {day.travel_notes && <p className="result_day_notes">{day.travel_notes}</p>}
                <ul className="result_day_items">
                  {(day.items || []).map((item, i) => (
                    <li key={i} className="result_day_item">
                      {item.time && <span className="result_day_time">{item.time}</span>}
                      <span className="result_day_item_title">{item.title}</span>
                      {item.duration_minutes != null && <span className="result_day_duration">{item.duration_minutes} min</span>}
                      {item.description && <span className="result_day_desc">{item.description}</span>}
                      {item.price != null && item.price > 0 && <span className="result_price result_price_small">{formatMoney(item.price, item.currency)}</span>}
                      <span className="result_day_links">
                        {item.map_link && <a href={item.map_link} target="_blank" rel="noopener noreferrer" className="result_link_small">Map</a>}
                        {item.booking_link && <a href={item.booking_link} target="_blank" rel="noopener noreferrer" className="result_link_small">Book</a>}
                      </span>
                    </li>
                  ))}
                </ul>
              </Card>
            ))}
          </div>
        </Section>
      ) : null}

      {bookings.length > 0 ? (
        <Section title="Booking links" icon="🔗">
          <div className="result_bookings">
            {bookings.map((b, i) => (
              <Card key={i} className="result_booking_card">
                <span className="result_booking_type">{b.type}</span>
                <span className="result_booking_label">{b.label}</span>
                {b.price != null && <span className="result_price">{formatMoney(b.price, b.currency)}</span>}
                <span className="result_link_group">
                  {b.booking_link && <a href={b.booking_link} target="_blank" rel="noopener noreferrer" className="result_link_btn">Book</a>}
                  {b.map_link && <a href={b.map_link} target="_blank" rel="noopener noreferrer" className="result_link_btn result_link_btn_secondary">Map</a>}
                </span>
              </Card>
            ))}
          </div>
        </Section>
      ) : null}

      {decisionLog.length > 0 ? (
        <Section title="Agent reasoning" icon="🧠">
          <Card className="result_log_card">
            <ul className="result_log">
              {decisionLog.map((e, i) => (
                <li key={i} className="result_log_entry">
                  <span className="result_log_agent">{e.agent}</span>
                  {e.step ? <span className="result_log_step">{e.step}</span> : null}
                  <span className="result_log_message">{e.message}</span>
                </li>
              ))}
            </ul>
          </Card>
        </Section>
      ) : null}

      {state && Object.keys(state).length > 0 && !intent && !researched && !budget && itinerary.length === 0 && bookings.length === 0 ? (
        <Card>
          <p className="result_fallback">Plan state received. No structured sections to display.</p>
        </Card>
      ) : null}
    </ResultWrapper>
  );
}

/**
 * Formatted, aesthetic display of the travel plan result (no raw JSON).
 */
export default function PlanResultView({
  status,
  state,
  onApprove,
  approving,
  interrupt,
}: PlanResultViewProps) {
  const s = (state || {}) as PlanState;
  const intent = s.parsed_intent;
  const researched = s.researched_data;
  const budget = s.budget_allocation || s.approved_budget;
  const itinerary = s.day_by_day_itinerary || [];
  const bookings = s.booking_options || [];
  const decisionLog = s.decision_log || [];
  const shortlist = s.destination_shortlist || [];

  const interruptPayload: InterruptPayload | undefined = interrupt?.[0] as InterruptPayload | undefined;

  if (status === "awaiting_approval" && interruptPayload) {
    const isBudget = interruptPayload.checkpoint === "budget_allocation";
    const isItinerary = interruptPayload.checkpoint === "final_itinerary";
    const isDest = interruptPayload.checkpoint === "destination_shortlist";
    const title =
      isDest ? "Confirm destinations" :
      isBudget ? "Confirm budget" :
      isItinerary ? "Confirm itinerary" :
      "Review & continue";

    return (
      <React.Fragment>
        <div className="result_wrapper">
          <div className="result_approval_card">
            <div className="result_approval_badge">Approval needed</div>
            <h2 className="result_approval_title">{title}</h2>
            <p className="result_approval_message">
              {interruptPayload.message || "Review the details below and approve to continue."}
            </p>
            {isDest && shortlist.length > 0 ? (
              <div className="result_approval_preview">
                <span className="result_approval_preview_label">Destinations</span>
                <div className="result_pills">
                  {shortlist.map((d) => (
                    <span key={d} className="result_pill">{d}</span>
                  ))}
                </div>
              </div>
            ) : null}
            {isBudget && interruptPayload.budget_allocation ? (
              <div className="result_approval_preview">
                <span className="result_approval_preview_label">Budget breakdown</span>
                <ul className="result_budget_list">
                  {["transport", "stay", "food", "activities", "buffer"].map((key) => {
                    const val = (interruptPayload.budget_allocation as Record<string, number>)[key];
                    if (val == null || val === 0) return null;
                    return (
                      <li key={key} className="result_budget_row">
                        <span className="result_budget_label">{key}</span>
                        <span className="result_budget_value">{formatMoney(val, interruptPayload.budget_allocation?.currency)}</span>
                      </li>
                    );
                  })}
                </ul>
              </div>
            ) : null}
            {isItinerary && interruptPayload.day_by_day_itinerary?.length ? (
              <div className="result_approval_preview">
                <span className="result_approval_preview_label">Itinerary</span>
                <p className="result_approval_itinerary_summary">
                  {interruptPayload.day_by_day_itinerary.length} day(s) planned.
                </p>
              </div>
            ) : null}
            {onApprove ? (
              <button
                type="button"
                className="result_approve_btn"
                onClick={onApprove}
                disabled={approving}
              >
                {approving ? "Sending…" : "Approve & continue"}
              </button>
            ) : null}
          </div>
        </div>
      </React.Fragment>
    );
  }

  return (
    <PlanResultContent
      intent={intent}
      shortlist={shortlist}
      researched={researched}
      budget={budget}
      itinerary={itinerary}
      bookings={bookings}
      decisionLog={decisionLog}
      state={s}
    />
  );
}
