# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- My initial UML design used four classes: `Owner`, `Pet`, `Task`, and `Scheduler`.
- `Owner` was responsible for managing a collection of pets and giving global access to tasks.
- `Pet` held species/name data and owned the list of tasks for that pet.
- `Task` represented an individual care action with metadata (time, priority, frequency, completion).
- `Scheduler` acted as the algorithmic layer that sorts, filters, detects conflicts, and marks completion.

**b. Design changes**

- Yes. I added a `due_date` attribute to `Task` so recurring tasks could create true "next-day" or "next-week" instances rather than reusing the same date.
- I also added serialization helpers (`to_dict`/`from_dict`) and owner-level `save_to_json`/`load_from_json` for persistence.
- Another change was making `Owner.get_all_tasks()` return `(Pet, Task)` pairs to simplify scheduler output formatting and filtering.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- The scheduler considers date, time, completion status, priority, recurrence frequency, and pet ownership.
- Sort order is `due_date -> time -> priority`.
- Conflict detection checks for exact duplicate date/time slots.
- Overlap detection checks real time windows using `duration_minutes`.
- Advanced logic adds weighted priority scheduling and a time-blocked non-overlapping plan.
- I prioritized constraints that directly impact daily usability for a pet owner: "what do I do next," "what overlaps," and "what repeats." 

**b. Tradeoffs**

- One tradeoff is that the time-blocked planner shifts tasks forward in fixed 15-minute increments rather than searching globally optimal schedules.
- This is reasonable because the behavior is deterministic, easy to debug, and understandable for end users.

---

## 3. AI Collaboration

**a. How you used AI**

- I used AI for class design scaffolding, method planning, and test generation.
- The most helpful prompts were explicit and code-aware, for example:
	- "Generate an OOP skeleton with dataclasses for Task and Pet."
	- "Suggest sorting and filtering algorithms for scheduler records."
	- "Create pytest cases for recurrence and conflict detection edge cases."

**b. Judgment and verification**

- I rejected an AI approach that overcomplicated the Streamlit integration with too many derived state containers.
- I replaced it with one owner object plus one scheduler object in `st.session_state`, then verified behavior through:
	- manual UI interaction,
	- CLI demo output from `main.py`,
	- automated pytest checks.

---

## 4. Testing and Verification

**a. What you tested**

- I tested:
	- task completion updates,
	- adding tasks to a pet,
	- chronological sorting,
	- daily recurrence creation,
	- conflict detection for duplicate times,
	- duration-based overlap conflict detection,
	- next available slot logic,
	- JSON save/load round trip.
- These are critical because they cover the main business logic that drives schedule correctness.

**b. Confidence**

- Confidence level: 4/5.
- Next edge cases to test:
	- invalid time formats from user input,
	- weekly recurrence across month/year boundaries,
	- behavior with large task volumes and many pets,
	- optional optimization for minimal total delay when resolving overlaps.

---

## 5. Reflection

**a. What went well**

- I am most satisfied with the modular architecture: business logic in `pawpal_system.py`, verification in `main.py`, and UI in `app.py`.

**b. What you would improve**

- In a second iteration, I would add user-defined hard constraints ("do not schedule after X") and a drag/drop UI to manually override generated plans.

**c. Key takeaway**

- A key takeaway is that AI is best used as a rapid drafting partner, while I remain the lead architect who validates tradeoffs, simplifies design, and verifies correctness with tests.

---

## 6. Prompt/Model Comparison

**a. Compared approaches**

- I compared two AI prompting strategies for implementing advanced scheduling:
	- Strategy A (broad): "Add advanced scheduling with overlap handling."
	- Strategy B (constrained): "Implement weighted priority sorting, duration-aware overlap detection, and 15-minute incremental rescheduling with deterministic outputs and pytest coverage."

**b. Which was better and why**

- Strategy B produced better results: clearer method boundaries, fewer ambiguous assumptions, and testable behavior.
- Strategy A often returned higher-level suggestions that required substantial manual refinement.

**c. What I kept/rejected**

- I kept constrained, modular suggestions that directly mapped to `Scheduler` methods.
- I rejected overly complex optimization-heavy suggestions because they reduced readability and were unnecessary for rubric goals.
