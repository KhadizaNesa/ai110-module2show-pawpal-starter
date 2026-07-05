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

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```
Main.py Sample output - 

=============================================
Today's Schedule for Maya
(Time available: 60 minutes)
=============================================

Pets:
  - Luna (cat, age 2) - 2 task(s)
  - Buddy (dog, age 4) - 3 task(s)

Planned tasks:
  1. Feed breakfast at 07:30 (daily, 10 min, priority 5) - not done
  2. Morning walk at 08:00 (daily, 30 min, priority 5) - not done
  3. Clean litter box at 12:00 (daily, 15 min, priority 3) - not done

Total time planned: 55 of 60 minutes
=============================================

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The automated tests confirm that PawPal+'s core scheduling logic works as
expected, so you can change the code and quickly see if anything breaks. They
cover both everyday use and trickier edge cases, including:

- **Task completion** — a task starts not-done and becomes done.
- **Adding tasks to a pet** — a pet's task list grows when a task is added.
- **Sorting tasks by priority and time** — most important first, and earliest first.
- **Daily plan generation** — the plan stays within the available time limit.
- **Filtering tasks** — by completion status and by pet.
- **Recurring tasks** — daily and weekly tasks create the correct next occurrence.
- **Conflict detection** — tasks with the same date and time are flagged.
- **Edge cases** — such as owners with no pets or pets with no tasks.

Sample test output:

```
================================ test session starts ================================
platform win32 -- Python 3.13.4, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\dibs1\Desktop\CodePath_summer26\ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 22 items

tests\test_pawpal.py ......................                                    [100%]

================================ 22 passed in 0.06s =================================
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks by scheduled time in `"HH:MM"` format, earliest first. |
| Filtering | `Scheduler.filter_by_completion()`, `Scheduler.filter_by_pet_name()` | Filters tasks by completion status or by pet name. |
| Conflict handling | `Scheduler.find_conflicts()` | Detects tasks that have the same due date and same scheduled time. |
| Recurring tasks | `Task.create_next_occurrence()`, `Scheduler.mark_task_complete()` | Creates the next daily or weekly task after a recurring task is marked complete. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
