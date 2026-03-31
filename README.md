# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The `Scheduler` class goes beyond a basic priority sort. Here is a summary of the features added during Module 2:

**Sort by time**
Tasks are ordered by earliest `latest_start_time` deadline first, then by descending priority within the same deadline bucket. Tasks with no deadline are placed last. This ensures time-sensitive tasks (e.g. morning medication at 07:30) are always scheduled before open-ended ones.

**Filter by pet or status**
`filter_tasks(pet_name, completed)` returns a filtered view of the task list in a single pass. Both parameters are optional — pass one, both, or neither. Useful for showing only Luna's pending tasks, or auditing everything that has been completed today.

**Recurring tasks**
Tasks can be marked `recurrence="daily"` or `recurrence="weekly"`. Calling `complete_task(title)` marks the task done and automatically appends a fresh copy to the queue with its next due date calculated using Python's `timedelta` — `+1 day` for daily, `+1 week` for weekly. The original task's deadline time (HH:MM) is preserved on the new occurrence.

**Conflict detection — full**
`detect_conflicts()` runs three checks and returns all findings as a list of messages:
- *Deadline miss* — a task's sequential start time would exceed its stated deadline.
- *Shared deadline* — two tasks claim the exact same `latest_start_time`.
- *Time-window overlap* — any two tasks (same pet or different pets) have overlapping `[start, end)` intervals.

**Conflict detection — lightweight**
`quick_conflict_check()` is a fast O(n × d) alternative that uses a minute-slot dictionary instead of pairwise comparison. It returns the first warning string it finds, or `None` if the schedule is clear. It never raises an exception — any internal error is caught and surfaced as a warning string, making it safe to call anywhere.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
