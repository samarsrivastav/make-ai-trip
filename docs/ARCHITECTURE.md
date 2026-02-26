# AI Travel Planning & Booking Agent – Backend Architecture

## 1. High-level system overview

```mermaid
flowchart TB
  subgraph client [Client]
    NextJS[Next.js Frontend]
  end

  subgraph backend [Python Backend]
    FastAPI[FastAPI Server]
    Router[Plan Router]
    LangGraph[LangGraph Workflow]
    State[GraphState]
    Checkpointer[InMemorySaver]
  end

  subgraph agents [Agents]
    Intent[Intent Parser]
    Research[Research Agent]
    Budget[Budget Optimizer]
    Planner[Itinerary Planner]
    Coordinator[Booking Coordinator]
  end

  subgraph data [Data Sources]
    Flights[Flight APIs]
    Hotels[Hotel APIs]
    Weather[Weather API]
    Places[Places / Activities]
  end

  NextJS -->|POST /api/plan| FastAPI
  FastAPI --> Router
  Router -->|invoke / approve| LangGraph
  LangGraph --> State
  LangGraph --> Checkpointer
  LangGraph --> Intent
  Intent --> Research
  Research --> Budget
  Budget --> Planner
  Planner --> Coordinator
  Research --> Flights
  Research --> Hotels
  Research --> Weather
  Research --> Places
  LangGraph -->|state + interrupt| Router
  Router -->|JSON response| NextJS
```

- **FastAPI** exposes `/api/plan` (create) and `/api/plan/{thread_id}/approve` (resume).
- **LangGraph** runs the workflow; **GraphState** holds all plan data; **InMemorySaver** persists state for human-in-the-loop.
- **Agents** read/write state; **Research** can call external **Data sources** (currently demo data).

---

## 2. Workflow orchestration (node flow)

```mermaid
flowchart LR
  START([Start]) --> Intent
  Intent --> Research
  Research --> ApproveDest[Approve Destinations]
  ApproveDest -->|"interrupt → resume"| Budget
  Budget --> ApproveBudget[Approve Budget]
  ApproveBudget -->|"interrupt → resume"| Planner
  Planner --> ApproveItin[Approve Itinerary]
  ApproveItin -->|"interrupt → resume"| Coordinator
  Coordinator --> END([End])
```

| Step | Node | Role |
|------|------|------|
| 1 | **intent** | Parse `user_input` → `parsed_intent`, `destination_shortlist` |
| 2 | **research** | Fetch flights, hotels, activities, weather → `researched_data` |
| 3 | **approve_destinations** | **Interrupt** – user approves destination shortlist |
| 4 | **budget** | Allocate budget → `budget_allocation` |
| 5 | **approve_budget** | **Interrupt** – user approves or edits budget |
| 6 | **planner** | Build day-by-day itinerary → `day_by_day_itinerary` |
| 7 | **approve_itinerary** | **Interrupt** – user approves final itinerary |
| 8 | **coordinator** | Build booking-ready options → `booking_options` |

All edges are sequential; the three **approve** nodes call `interrupt()` so the graph pauses until the client sends a resume (e.g. `POST .../approve` with `resume: true`).

---

## 3. Agent roles and responsibilities

```mermaid
flowchart TB
  subgraph intent_agent [Intent Parser]
    I1[Parse user_input]
    I2[Extract destination, origin, budget, days]
    I3[Extract style, interests]
    I1 --> I2 --> I3
  end

  subgraph research_agent [Research Agent]
    R1[Use parsed_intent]
    R2[Fetch flights, hotels, activities, weather]
    R3[Write researched_data + decision_log]
    R1 --> R2 --> R3
  end

  subgraph budget_agent [Budget Optimizer]
    B1[Read budget_total from intent]
    B2[Allocate transport, stay, food, activities, buffer]
    B3[Write budget_allocation + decision_log]
    B1 --> B2 --> B3
  end

  subgraph planner_agent [Itinerary Planner]
    P1[Read num_days, destination]
    P2[Build DayPlan per day with timings]
    P3[Write day_by_day_itinerary + decision_log]
    P1 --> P2 --> P3
  end

  subgraph coord_agent [Booking Coordinator]
    C1[Read researched_data]
    C2[Build BookingOption with links]
    C3[Write booking_options + decision_log]
    C1 --> C2 --> C3
  end

  intent_agent --> research_agent
  research_agent --> budget_agent
  budget_agent --> planner_agent
  planner_agent --> coord_agent
```

| Agent | Inputs | Outputs |
|-------|--------|--------|
| **Intent Parser** | `user_input` | `parsed_intent`, `destination_shortlist`, `decision_log` |
| **Research** | `parsed_intent` | `researched_data` (flights, hotels, activities, weather, tips), `decision_log` |
| **Budget Optimizer** | `parsed_intent` | `budget_allocation`, `decision_log` |
| **Planner** | `parsed_intent`, `researched_data` | `day_by_day_itinerary`, `decision_log` |
| **Booking Coordinator** | `researched_data` | `booking_options`, `decision_log` |

---

## 4. Human-in-the-loop integration

```mermaid
sequenceDiagram
  participant User
  participant Frontend
  participant API
  participant Graph

  User->>Frontend: Enter trip request + Create plan
  Frontend->>API: POST /api/plan { user_input }
  API->>Graph: invoke(inputs, config thread_id)
  Graph->>Graph: intent → research
  Graph->>API: return state + __interrupt__
  API->>Frontend: 200 { status: awaiting_approval, interrupt, state }
  Frontend->>User: Show "Approve destinations?"

  User->>Frontend: Approve & continue
  Frontend->>API: POST /api/plan/{id}/approve { resume: true }
  API->>Graph: invoke(Command(resume=true), same thread_id)
  Graph->>Graph: budget → approve_budget (interrupt)
  Graph->>API: return state + __interrupt__
  API->>Frontend: 200 { status: awaiting_approval, interrupt, state }
  Frontend->>User: Show "Approve budget?"

  User->>Frontend: Approve & continue
  Frontend->>API: POST /api/plan/{id}/approve { resume: true }
  API->>Graph: invoke(Command(resume=true), same thread_id)
  Graph->>Graph: planner → approve_itinerary (interrupt)
  Graph->>API: return state + __interrupt__
  Frontend->>User: Show "Approve itinerary?"

  User->>Frontend: Approve & continue
  Frontend->>API: POST /api/plan/{id}/approve { resume: true }
  API->>Graph: invoke(Command(resume=true), same thread_id)
  Graph->>Graph: coordinator → END
  Graph->>API: return state, no interrupt
  API->>Frontend: 200 { status: complete, state }
  Frontend->>User: Show full plan + booking links
```

- **Checkpoints**: (1) destination shortlist, (2) budget allocation, (3) final itinerary.
- **Resume**: Same `thread_id` + `Command(resume=...)` so the graph continues from the interrupt.
- **Checkpointer**: InMemorySaver stores state per `thread_id` so resume has full context.

---

## 5. State schema (GraphState)

```mermaid
flowchart LR
  subgraph state [GraphState]
    user_input[user_input]
    parsed_intent[parsed_intent]
    destination_shortlist[destination_shortlist]
    researched_data[researched_data]
    budget_allocation[budget_allocation]
    approved_budget[approved_budget]
    day_by_day_itinerary[day_by_day_itinerary]
    booking_options[booking_options]
    decision_log[decision_log]
    current_checkpoint[current_checkpoint]
  end
```

- **user_input**: Raw string from the user.
- **parsed_intent**: ParsedIntent (budget_total, currency, origin, destination, num_days, travel_style, interests).
- **researched_data**: ResearchedData (flights[], hotels[], activities[], weather[], local_tips).
- **budget_allocation** / **approved_budget**: BudgetAllocation (transport, stay, food, activities, buffer, reasoning).
- **day_by_day_itinerary**: DayPlan[] (day, date, items[] with time, title, duration, price, links).
- **booking_options**: BookingOption[] (type, label, booking_link, map_link, price).
- **decision_log**: DecisionLogEntry[] (agent, step, message) for transparency.

---

## 6. API surface

| Method | Path | Purpose |
|--------|------|--------|
| POST | `/api/plan` | Create plan: body `{ user_input }` → runs graph; returns `thread_id`, `status`, `state`, optional `interrupt` |
| POST | `/api/plan/{thread_id}/approve` | Resume: body `{ resume: true }` or `{ resume: <modified_budget> }` → continues graph |
| GET | `/api/plan/{thread_id}` | Get current state for a thread (e.g. reload page) |
| GET | `/health` | Health check |

---

## 7. File layout (backend)

```
backend/
├── main.py           # FastAPI app, CORS, lifespan
├── graph.py          # LangGraph definition, nodes, edges, interrupts, checkpointer
├── state.py          # GraphState, Pydantic models (ParsedIntent, ResearchedData, etc.)
├── routes.py         # POST /api/plan, POST /api/plan/{id}/approve, GET /api/plan/{id}
├── agents/
│   ├── intent.py     # parse_intent (regex + keywords)
│   ├── research.py   # research (demo data; pluggable APIs)
│   ├── budget.py     # optimize_budget
│   ├── planner.py    # plan_itinerary
│   └── coordinator.py # coordinate_bookings
└── requirements.txt
```

This document describes the LLM/backend architecture for the AI Travel Planning & Booking Agent.
