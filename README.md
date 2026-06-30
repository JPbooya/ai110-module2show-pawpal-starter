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

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

python3 main.py
Today's Schedule
--------------------
07:30 — Feeding
08:00 — Morning walk
18:00 — Evening walk

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.organize_by_time(day_of_week=None)` | Sorts tasks chronologically by their `time` attribute. Can be scoped to just a given weekday's due tasks; defaults to all tasks across all pets. |
| Filtering | `Scheduler.filter_tasks(pet_name=None, status=None)` | Filters tasks by pet name and/or completion status (`"pending"` or `"completed"`). Both filters combine with AND when given together. |
| Conflict detection | `Scheduler.find_conflicts(day_of_week=None)`, `Scheduler.check_for_conflicts(day_of_week=None)` | Two strategies, traded off for accuracy vs. robustness: `find_conflicts` does duration-aware overlap detection via `Task.overlaps()`/`start_minutes()`/`end_minutes()`, catching partial overlaps but raising on a malformed `time` string. `check_for_conflicts` is a lightweight version that groups tasks by exact start time only (no parsing, can't raise) and returns a ready-to-display warning string — used in `app.py` since it can't crash on bad user input. Both check tasks belonging to the same pet *or* different pets. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.complete_task(task)`, `Task.is_due_on(day_of_week)` | Completing a `daily`/`weekly` task through `Scheduler.complete_task()` marks the original as done and automatically appends a fresh pending instance (`Task.next_occurrence()`) to the same pet, so the original stays as a historical record. `Task.is_due_on()` determines whether a recurring task applies on a given weekday (`weekly` tasks only match their assigned `day_of_week`; `daily`/`once` are always due). |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
