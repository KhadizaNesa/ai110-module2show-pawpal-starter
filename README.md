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
- **Next available slot** — finds the earliest free start time, using gaps between tasks and falling back to after the last task.
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
This was the initial test suite that verified the basic functionality of the project, including task completion and adding tasks to a pet.

```text
====================================== test session starts =======================================
platform win32 -- Python 3.13.4, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\dibs1\Desktop\CodePath_summer26\ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 2 items

tests\test_pawpal.py ..                                                                     [100%]

======================================= 2 passed in 0.03s ========================================
```
## 📐 Smarter Scheduling


| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks by scheduled time in `"HH:MM"` format, earliest first. |
| Priority scheduling | `Scheduler.sort_by_priority_then_time()` | Sorts by priority level (High → Low) first, then by time within each level. Used by `generate_daily_plan()`. |
| Filtering | `Scheduler.filter_by_completion()`, `Scheduler.filter_by_pet_name()` | Filters tasks by completion status or by pet name. |
| Conflict handling | `Scheduler.find_conflicts()` | Detects tasks that have the same due date and same scheduled time. |
| Recurring tasks | `Task.create_next_occurrence()`, `Scheduler.mark_task_complete()` | Creates the next daily or weekly task after a recurring task is marked complete. |
| Rescheduling overdue tasks | `Scheduler.reschedule_overdue_tasks()` | Rolls overdue, not-done tasks forward: daily tasks jump to today, weekly tasks advance in 7-day steps (keeping their weekday). |
| Next available slot | `Scheduler.find_next_available_slot()` | Finds the earliest free `"HH:MM"` start time where a task of a given duration would fit. |

### 🕒 Next Available Time Slot

`Scheduler.find_next_available_slot(owner, duration_minutes)` answers the
question *"When is the soonest I can fit in a new task?"*

The day is treated as starting at **08:00**. The scheduler gathers every task
the owner has, sorts them by time, and scans the day for the first free gap
big enough to hold a task of the requested duration.

**Rules**

- If the owner has **no tasks**, it returns `"08:00"`.
- If there is a **gap large enough** (before the first task or between two
  tasks), it returns the start time of that gap.
- If **no gap is large enough**, it returns the time right after the final
  task finishes.

**Example**

```python
from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner(name="Sam")
rex = Pet(name="Rex", species="dog", age=3)
owner.add_pet(rex)
rex.add_task(Task("Morning walk", "08:00", "daily", priority=5, duration_minutes=30))
rex.add_task(Task("Vet call", "10:00", "daily", priority=4, duration_minutes=20))

scheduler = Scheduler()
print(scheduler.find_next_available_slot(owner, duration_minutes=30))
# -> "08:30"  (the walk ends at 08:30, leaving room before the 10:00 vet call)
```

## 🎨 Professional UI and Output Formatting

PawPal+ prints a polished command-line interface instead of raw Python objects.
All of the presentation code lives in its own module, **`formatting.py`**, so the
logic layer (`pawpal_system.py`) stays clean.

**Formatting features**

- **Structured CLI tables** — task lists and the daily plan are drawn as neat,
  aligned tables using the **`tabulate`** library (the `rounded_grid` style).
- **Emojis for task types** — the task description is scanned for keywords and
  given a matching emoji: 🚶 walk, 🍽️ feed, 💊 medicine, 🏥 vet, 🛁 groom/bath,
  🎾 play, 🧹 litter/clean, 💧 water, 🎓 train, 📸 photo, and 🐾 as a fallback.
- **Color-coded priority badges** — priority levels are colored with
  **`colorama`** (which works on Windows too): **High** is red, **Medium** is
  yellow, and **Low** is green.
- **Status indicators** — done tasks show ✅ and a green "done"; not-done tasks
  show ⬜ and a dimmed "not done".
- **Color-coded summary & headings** — section headings are bold cyan, and the
  plan's time-summary line turns green when the plan fits and yellow when it is
  full.

**Functions and libraries used**

| Feature | Function (in `formatting.py`) | Library |
|---------|-------------------------------|---------|
| Structured tables | `format_task_table()`, `format_plan()` | `tabulate` |
| Task-type emoji | `task_emoji()` | (plain Python) |
| Status icon (✅ / ⬜) | `status_icon()` | (plain Python) |
| Color-coded priority | `priority_badge()` | `colorama` |
| Colored status text | `status_text()` | `colorama` |
| Section headings | `format_heading()` | `colorama` |

> Install the new libraries with `pip install -r requirements.txt`
> (`tabulate` and `colorama` were added).

**Sample CLI output** (run `python main.py` — colors show in a real terminal):

```text
✨ Planned tasks:
╭───────┬────────┬────────────────┬────────┬────────────┬────────────┬──────────╮
│       │ Time   │ Task           │ Freq   │ Priority   │ Duration   │ Status   │
├───────┼────────┼────────────────┼────────┼────────────┼────────────┼──────────┤
│ ⬜ 🍽️ │ 07:30  │ Feed breakfast │ daily  │ High       │ 10 min     │ not done │
├───────┼────────┼────────────────┼────────┼────────────┼────────────┼──────────┤
│ ⬜ 💊 │ 08:00  │ Give medicine  │ daily  │ High       │ 5 min      │ not done │
├───────┼────────┼────────────────┼────────┼────────────┼────────────┼──────────┤
│ ⬜ 🚶 │ 08:00  │ Morning walk   │ daily  │ High       │ 30 min     │ not done │
╰───────┴────────┴────────────────┴────────┴────────────┴────────────┴──────────╯

Total time planned: 45 of 60 minutes
```

The Streamlit app (`app.py`) reuses `task_emoji()` and `status_icon()` so the
web task table shows the same icons.

## ⭐ Advanced Priority Scheduling

PawPal+ goes beyond simple time sorting. Every task has a **priority level** —
**Low**, **Medium**, or **High** — and the scheduler orders tasks by
**priority first, then by time**.

**How it works**

- A priority *level* (a word) maps to a *number* where higher means more
  important: `Low = 1`, `Medium = 3`, `High = 5`. The helpers
  `priority_from_level("High")` and `priority_to_label(5)` convert between the
  word and the number.
- `Scheduler.sort_by_priority_then_time(tasks)` sorts with the key
  `(-priority, time)`: Python compares the tuple left-to-right, so it settles
  priority before it ever looks at the time. Higher priority comes first, and
  tasks that share a priority fall back to earliest-time-first.
- `Scheduler.generate_daily_plan()` now uses this combined ordering, so the
  most important tasks are always scheduled first — even if a lower-priority
  task happens earlier in the day.

**CLI output examples**

Running `python pawpal_system.py` builds one pet with four tasks (a High task
at 18:00, a Low task at 08:15, a High task at 08:00, and a Medium task at
10:00) and prints the difference between the two orderings:

```text
Sorted by time only (old behavior):
  08:00  Morning walk   [High]
  08:15  Scoop litter   [Low]
  10:00  Vet call       [Medium]
  18:00  Give medicine  [High]

Sorted by priority, then time (advanced scheduling):
  08:00  Morning walk   [High]
  18:00  Give medicine  [High]
  10:00  Vet call       [Medium]
  08:15  Scoop litter   [Low]

Daily plan for Sam (60 minutes available):
  - Morning walk at 08:00 (daily, 30 min, priority High) - not done
  - Give medicine at 18:00 (daily, 5 min, priority High) - not done
  - Vet call at 10:00 (weekly, 20 min, priority Medium) - not done
```

Notice how in the **priority-then-time** ordering both `High` tasks jump ahead
of the `Medium` and `Low` tasks, and within the `High` group the earlier 08:00
walk comes before the 18:00 medicine. Plain time sorting would have listed the
`Low` "Scoop litter" second, which is not what a busy owner wants.

## 💾 Data Persistence

PawPal+ remembers your pets and tasks between runs by saving them to a file
called **`data.json`** in the project folder.

**How it works**

- Because JSON can only store plain values (strings, numbers, lists, and
  dictionaries), each object first converts itself into a dictionary:
  `Owner.to_dict()` includes every pet, `Pet.to_dict()` includes every task,
  and `Task.to_dict()` includes all task fields (`description`, `time`,
  `frequency`, `priority`, `duration_minutes`, `due_date`, and `completed`).
- The `due_date` is a Python `date`, which JSON cannot store directly, so it is
  saved as a `"YYYY-MM-DD"` string and turned back into a real `date` when
  loaded.
- **Saving:** `Owner.save_to_json("data.json")` writes the owner (with all pets
  and tasks) to `data.json`. In the Streamlit app, click **💾 Save data**.
- **Loading:** `Owner.load_from_json("data.json")` rebuilds the owner from the
  file using `Owner.from_dict()` / `Pet.from_dict()` / `Task.from_dict()`. The
  app loads this data automatically when it starts.
- If `data.json` does not exist yet (for example, the very first run),
  `load_from_json()` simply returns a new, empty `Owner` instead of raising an
  error.

**Methods added**

| Purpose | Method(s) |
|---------|-----------|
| Object → dictionary | `Task.to_dict()`, `Pet.to_dict()`, `Owner.to_dict()` |
| Dictionary → object | `Task.from_dict()`, `Pet.from_dict()`, `Owner.from_dict()` |
| Save / load file | `Owner.save_to_json(filename="data.json")`, `Owner.load_from_json(filename="data.json")` |

**Files modified**

- `pawpal_system.py` — added the `to_dict` / `from_dict` conversion methods and
  the `save_to_json` / `load_from_json` persistence methods.
- `app.py` — loads the owner from `data.json` on startup and adds a
  **💾 Save data** button.
- `tests/test_pawpal.py` — added tests for the dictionary round trips, the
  save/load round trip, and the missing-file case.
- `README.md` — added this Data Persistence section.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. Enter the owner's name to create or update the owner profile in the application.

2. Add a pet by entering the pet's name, selecting its species, and entering its age. The pet is stored in the system and can have multiple care tasks.

3. Add care tasks for the selected pet, including the task description, scheduled time, priority, duration, and recurrence (daily or weekly).

4. Enter the number of minutes available for pet care and click **Generate Schedule**. The Scheduler creates a daily plan based on task priority, available time, and completion status.

5. Review the generated schedule. Tasks are displayed in chronological order, can be filtered by pet or completion status, and any scheduling conflicts are shown as warnings. When a recurring task is marked complete, the Scheduler automatically creates the next daily or weekly occurrence.

### Sample CLI Output

```text
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
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
