# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Add a new scheduling algorithm to PawPal+: a `Scheduler` method
`find_next_available_slot(owner, duration_minutes)` that looks at all scheduled
tasks sorted by time and returns the first available time slot where a task of
the requested duration would fit. It should return `"08:00"` when no tasks
exist, and the next available time after the final task when no gap is large
enough. Requirements included keeping it beginner-friendly, adding docstrings,
adding pytest tests, and updating the README.

**What did the agent do?**

- Read `app.py`, `pawpal_system.py`, `tests/test_pawpal.py`, and `README.md`
  to understand the existing structure before making changes.
- Added a `DAY_START = "08:00"` constant and two helper functions,
  `_time_to_minutes` and `_minutes_to_time`, to `pawpal_system.py`.
- Implemented `Scheduler.find_next_available_slot(owner, duration_minutes)`,
  which sorts the owner's tasks by time (reusing the existing `sort_by_time`)
  and walks a cursor through the day to find the first gap large enough for the
  new task.
- Added 5 pytest tests to `tests/test_pawpal.py` covering: no tasks, a gap
  before the first task, a gap between two tasks, no gap large enough, and a
  gap that is too small to use.
- Ran `python -m pytest` — all 27 tests passed (22 original + 5 new).
- Documented the feature in `README.md` (table row, a dedicated section with
  rules and a runnable example, and a test-coverage bullet).

**What did you have to verify or fix manually?**

The agent flagged one design choice for review: the day is anchored at `08:00`
as both the default and the earliest suggested time, so the method will not
propose a slot before `08:00` (tasks scheduled earlier are still handled safely
because the cursor only moves forward). This matched the requirements and the
app's sample data, so no change was needed.

---

## Prompt Comparison (SF11)

> Compare two different models on the same complex algorithmic task.

### The task (the same prompt given to both models)

> Add a `Scheduler` method
> `reschedule_overdue_tasks(owner, today=None)` to PawPal+. It should roll every
> **overdue, not-completed, repeating** task forward to its next valid date:
> - a `daily` task jumps to `today`;
> - a `weekly` task advances in whole **7-day steps** until it lands on or after
>   `today`, so it stays on the **same weekday** it was originally booked for;
> - `completed` tasks and non-repeating (one-off) tasks are left untouched.
>
> Return a list of `(task, old_date, new_date)` for every task that moved. Keep
> it beginner-friendly, add a docstring, and write pytest tests. A task is
> "overdue" when it is not done and its `due_date` is before `today`.

This is a good comparison task because the **weekly** rule is easy to get subtly
wrong: the naive fix ("just set the due date to today") loses the task's
weekday, which matters for something like a Monday grooming appointment.

### Side-by-side comparison

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Claude (Opus 4.8, via Claude Code) | _<!-- e.g. Gemini 2.5 Pro / ChatGPT (GPT-5) / GitHub Copilot — fill in -->_ |
| **Prompt** | The task prompt above (identical for both models). | The task prompt above (identical for both models). |
| **Response summary** | Implemented `reschedule_overdue_tasks` on `Scheduler`. Daily tasks are set to `today`; weekly tasks use a `while new_date < today: new_date += timedelta(days=7)` loop to preserve the weekday; completed / non-repeating tasks are skipped with `continue`. Returns a list of `(task, old_date, new_date)` tuples. Added 4 pytest tests, including one that asserts a Thursday weekly task lands on the next Thursday (`2026-06-25` → `2026-07-09`). | _<!-- Paste a 2–4 sentence summary of the other model's actual answer here. -->_ |
| **What was useful** | Correctly handled the weekday-preservation subtlety with the 7-day-step loop (not a naive reset). Skipped completed/one-off tasks as specified. Made `today` an injectable parameter (defaults to `date.today()`), which made the behavior deterministic and testable. Reused the existing `date`/`timedelta` imports and matched the file's heavily-commented, beginner-friendly style. | _<!-- What did the other model do well? -->_ |
| **Problems noticed** | Does **not** detect or resolve new **conflicts** created by rescheduling (two moved tasks can land in the same day+time slot); the caller must run `find_conflicts` afterward. Returns bare tuples rather than a small named result type, so callers must remember the tuple order. Does not automatically persist the changes to `data.json` — you must call `save_to_json` yourself. | _<!-- What was flawed, wrong, or missing? -->_ |
| **Decision** | ✅ **Chosen and shipped.** | _<!-- Chosen / not chosen — and one reason. -->_ |

### Which approach did you use in your final implementation and why?

I used **Option A (Claude)** and it is implemented in
`Scheduler.reschedule_overdue_tasks` in `pawpal_system.py`, with tests in
`tests/test_pawpal.py` (`test_reschedule_*`). The deciding factor was that it got
the **weekly weekday-preservation** rule right — the part of the spec most likely
to be handled incorrectly — and it exposed `today` as a parameter so the logic is
fully testable without depending on the real calendar date.

I noted its gaps (no automatic conflict resolution, no auto-save) as follow-up
work rather than blockers, since the task prompt only asked for the rescheduling
move itself. Conflict detection already exists separately (`find_conflicts`) and
saving is a separate, explicit step (`save_to_json`).

> _Reviewer note: Option B is left as a template. Paste the **actual** response
> you get from the second model (Gemini / ChatGPT / Copilot) into the cells
> marked with `<!-- ... -->`, then update the Decision row and this paragraph if
> the comparison changes your choice._
