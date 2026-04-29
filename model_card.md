# PawPal+ Model Card

## System Type
PawPal+ is an applied AI scheduling assistant for pet care. It uses an agentic planning loop: natural-language instructions are parsed into task drafts, validated against the current schedule, repaired if needed, and then previewed for human approval.

## Intended Use
Use PawPal+ to plan recurring or one-time pet care tasks such as feeding, walks, medication, training, and enrichment. It is designed for personal organization and demo purposes, not medical or veterinary decision-making.

## What the AI Does
The agent:
- parses messy instructions into structured tasks
- extracts pets, times, frequencies, priorities, and durations
- checks for exact conflicts and duration-based overlaps
- shifts tasks forward in 15-minute increments when needed
- assigns a confidence score and explanation

## Data and Inputs
Inputs are user-authored pet-care requests, the current in-app schedule, and saved local JSON data. The system does not use external retrieval or third-party knowledge sources.

## Reliability and Evaluation
Validation is built into the app through:
- automated pytest coverage for scheduling, persistence, recurrence, and agentic planning
- conflict and overlap detection
- confidence scoring for generated plans
- logging of planning and rescheduling events

Current test status: 10/10 tests passing.

## Limitations
- The parser is rule-based, so it can miss unusual phrasing or ambiguous instructions.
- The planner uses deterministic heuristics instead of a large language model API.
- It cannot reason about real-world veterinary constraints, location, or pet health records.
- It may over-repair when multiple tasks are intentionally close together.

## Bias and Safety Considerations
The app is optimized for schedule clarity, not medical advice. To reduce misuse:
- it labels confidence explicitly
- it shows warnings and repair behavior
- it keeps human approval in the loop before applying plans
- it avoids claims beyond scheduling assistance

## Human Collaboration With AI
Helpful suggestion: AI helped identify that the scheduler should stay deterministic and testable instead of becoming a complex optimization engine.
Flawed suggestion: AI suggested a broader retrieval-based design, but PawPal does not need external knowledge lookup, so that direction was rejected.

## What Surprised Me
The most useful result was how much trust improved once the planner was forced to explain its decisions and repair conflicts in a deterministic way.

## Ethical Notes
This project should not be presented as a pet-health or vet-advice system. It is a productivity tool for organizing care routines, with guardrails and human review built in.
