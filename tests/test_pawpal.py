"""Beginner-friendly unit tests for the PawPal+ system.

Run them from the project root with:
    pytest

Each test follows a simple "Arrange, Act, Assert" pattern:
    1. Arrange - set up the objects we need.
    2. Act     - do the thing we want to test.
    3. Assert  - check that the result is what we expect.
"""

from datetime import date, timedelta

from pawpal_system import (
    Task,
    Pet,
    Owner,
    Scheduler,
    priority_from_level,
    priority_to_label,
)
from formatting import (
    task_emoji,
    status_icon,
    priority_badge,
    format_task_table,
    format_plan,
)


def test_task_completion():
    """A task should start incomplete and become complete after mark_complete()."""

    # Arrange: create a single task.
    task = Task(
        description="Morning walk",
        time="08:00",
        frequency="daily",
        priority=5,
        duration_minutes=30,
    )

    # Assert: a brand-new task has not been done yet.
    assert task.completed is False

    # Act: mark the task as done.
    task.mark_complete()

    # Assert: the task is now marked complete.
    assert task.completed is True


def test_task_addition():
    """Adding a task to a pet should increase the pet's task count."""

    # Arrange: create a pet (it should start with no tasks).
    pet = Pet(name="Rex", species="dog", age=3)

    # Assert: a new pet begins with zero tasks.
    assert len(pet.get_tasks()) == 0

    # Arrange: create a task to add.
    task = Task(
        description="Feed breakfast",
        time="08:30",
        frequency="daily",
        priority=5,
        duration_minutes=10,
    )

    # Act: add the task to the pet.
    pet.add_task(task)

    # Assert: the pet now has exactly one task.
    assert len(pet.get_tasks()) == 1

    # Assert (optional): the task we added is actually in the pet's list.
    assert task in pet.get_tasks()


def test_task_default_due_date_is_today():
    """A task with no due_date given should default to today's date."""

    # Arrange & Act: create a task without passing due_date.
    task = Task(
        description="Feed breakfast",
        time="07:30",
        frequency="daily",
        priority=5,
        duration_minutes=10,
    )

    # Assert: due_date defaulted to today.
    assert task.due_date == date.today()


def test_daily_task_creates_next_occurrence_one_day_later():
    """A daily task's next occurrence is due the next day and not completed."""

    # Arrange: a completed daily task with a known due date.
    today = date(2026, 7, 4)
    task = Task(
        description="Feed breakfast",
        time="07:30",
        frequency="daily",
        priority=5,
        duration_minutes=10,
        completed=True,
        due_date=today,
    )

    # Act: ask for the next occurrence.
    next_task = task.create_next_occurrence()

    # Assert: it exists, is due one day later, and copies the details.
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False
    assert next_task.description == task.description
    assert next_task.frequency == "daily"


def test_weekly_task_creates_next_occurrence_seven_days_later():
    """A weekly task's next occurrence is due seven days later."""

    # Arrange: a weekly task with a known due date.
    today = date(2026, 7, 4)
    task = Task(
        description="Vet appointment",
        time="10:30",
        frequency="weekly",
        priority=4,
        duration_minutes=25,
        due_date=today,
    )

    # Act & Assert: next occurrence is 7 days out.
    next_task = task.create_next_occurrence()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=7)


def test_non_repeating_task_returns_none():
    """A task that is neither daily nor weekly has no next occurrence."""

    # Arrange: a one-off task.
    task = Task(
        description="Adopt-day photo",
        time="09:00",
        frequency="once",
        priority=1,
        duration_minutes=5,
    )

    # Act & Assert: nothing to repeat.
    assert task.create_next_occurrence() is None


def test_mark_task_complete_adds_next_task_to_pet():
    """mark_task_complete should complete the task and add its next occurrence."""

    # Arrange: a pet with one daily task, and a scheduler.
    pet = Pet(name="Luna", species="cat", age=2)
    task = Task(
        description="Feed breakfast",
        time="07:30",
        frequency="daily",
        priority=5,
        duration_minutes=10,
    )
    pet.add_task(task)
    scheduler = Scheduler()

    # Act: complete the task through the scheduler.
    new_task = scheduler.mark_task_complete(pet, task)

    # Assert: original is done, a new task was returned and added to the pet.
    assert task.completed is True
    assert new_task is not None
    assert len(pet.get_tasks()) == 2
    assert new_task in pet.get_tasks()


def test_find_conflicts_flags_same_time_across_pets():
    """Two pets booked at the same day and time should produce one warning."""

    # Arrange: an owner with two pets, each with a task at 08:00 today.
    owner = Owner(name="Maya")
    luna = Pet(name="Luna", species="cat", age=2)
    buddy = Pet(name="Buddy", species="dog", age=4)
    owner.add_pet(luna)
    owner.add_pet(buddy)

    luna.add_task(Task("Give medicine", "08:00", "daily", priority=4, duration_minutes=5))
    buddy.add_task(Task("Morning walk", "08:00", "daily", priority=5, duration_minutes=30))

    # Act: look for conflicts.
    warnings = Scheduler().find_conflicts(owner)

    # Assert: exactly one conflict, and it names both tasks.
    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Give medicine" in warnings[0]
    assert "Morning walk" in warnings[0]


def test_find_conflicts_returns_empty_when_times_differ():
    """Tasks at different times should not be reported as conflicts."""

    # Arrange: one pet with two tasks at different times.
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)
    rex.add_task(Task("Morning walk", "08:00", "daily", priority=5, duration_minutes=30))
    rex.add_task(Task("Evening play", "18:00", "daily", priority=2, duration_minutes=20))

    # Act & Assert: no clash, so no warnings.
    assert Scheduler().find_conflicts(owner) == []


# ---------------------------------------------------------------------------
# Core behavior 1: tasks are sorted by priority (higher number first).
# ---------------------------------------------------------------------------
def test_sort_by_priority_orders_high_to_low():
    """sort_tasks_by_priority should list the most important task first."""

    # Arrange: three tasks with mixed priorities.
    low = Task("Brush coat", "18:00", "weekly", priority=1, duration_minutes=15)
    high = Task("Give medicine", "08:00", "daily", priority=5, duration_minutes=5)
    mid = Task("Vet call", "10:00", "weekly", priority=3, duration_minutes=20)
    scheduler = Scheduler()

    # Act: sort them by priority.
    ordered = scheduler.sort_tasks_by_priority([low, high, mid])

    # Assert: highest priority comes first, lowest last.
    assert ordered == [high, mid, low]


def test_sort_by_priority_does_not_change_original_list():
    """sort_tasks_by_priority returns a new list and leaves the input untouched."""

    # Arrange: a list in a known order.
    first = Task("A", "08:00", "daily", priority=1, duration_minutes=5)
    second = Task("B", "09:00", "daily", priority=5, duration_minutes=5)
    original = [first, second]
    scheduler = Scheduler()

    # Act: sort it.
    scheduler.sort_tasks_by_priority(original)

    # Assert: the caller's list is still in its original order.
    assert original == [first, second]


# ---------------------------------------------------------------------------
# Core behavior 2: generate_daily_plan only includes tasks that fit the time.
# ---------------------------------------------------------------------------
def test_daily_plan_includes_only_tasks_that_fit():
    """generate_daily_plan should stay within the available minutes."""

    # Arrange: one pet with tasks that add up to more than the budget.
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)
    rex.add_task(Task("Walk", "08:00", "daily", priority=5, duration_minutes=30))
    rex.add_task(Task("Feed", "08:30", "daily", priority=4, duration_minutes=10))
    rex.add_task(Task("Groom", "18:00", "weekly", priority=1, duration_minutes=60))

    # Act: build a plan with only 45 minutes available.
    plan = Scheduler().generate_daily_plan(owner, available_minutes=45)

    # Assert: the walk (30) and feed (10) fit; the 60-min groom does not.
    total_minutes = sum(task.duration_minutes for task in plan)
    assert total_minutes <= 45
    descriptions = [task.description for task in plan]
    assert "Walk" in descriptions
    assert "Feed" in descriptions
    assert "Groom" not in descriptions


def test_daily_plan_orders_higher_priority_first():
    """generate_daily_plan should list higher-priority tasks earlier."""

    # Arrange: two tasks that both fit, with different priorities.
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)
    rex.add_task(Task("Low job", "09:00", "daily", priority=2, duration_minutes=10))
    rex.add_task(Task("High job", "08:00", "daily", priority=5, duration_minutes=10))

    # Act: build a plan with plenty of time.
    plan = Scheduler().generate_daily_plan(owner, available_minutes=60)

    # Assert: the higher-priority task comes first.
    assert plan[0].description == "High job"
    assert plan[1].description == "Low job"


# ---------------------------------------------------------------------------
# Core behavior 5: sort_by_time returns tasks in chronological order.
# ---------------------------------------------------------------------------
def test_sort_by_time_orders_earliest_first():
    """sort_by_time should order zero-padded HH:MM times from earliest to latest."""

    # Arrange: three tasks given out of order (note the zero-padded times).
    evening = Task("Evening play", "18:00", "daily", priority=2, duration_minutes=20)
    morning = Task("Morning walk", "08:00", "daily", priority=5, duration_minutes=30)
    midday = Task("Vet call", "10:00", "weekly", priority=3, duration_minutes=20)

    # Act: sort them by time.
    ordered = Scheduler().sort_by_time([evening, morning, midday])

    # Assert: earliest time first, latest time last.
    assert [task.time for task in ordered] == ["08:00", "10:00", "18:00"]


# ---------------------------------------------------------------------------
# Edge case: an owner with no pets.
# ---------------------------------------------------------------------------
def test_daily_plan_empty_when_owner_has_no_pets():
    """An owner with no pets should produce an empty plan."""

    # Arrange: an owner with no pets at all.
    owner = Owner(name="Lonely")

    # Act: try to build a plan.
    plan = Scheduler().generate_daily_plan(owner, available_minutes=60)

    # Assert: nothing to schedule.
    assert plan == []


# ---------------------------------------------------------------------------
# Edge case: a pet with no tasks.
# ---------------------------------------------------------------------------
def test_daily_plan_empty_when_pet_has_no_tasks():
    """An owner whose only pet has no tasks should produce an empty plan."""

    # Arrange: an owner with one pet that has zero tasks.
    owner = Owner(name="Sam")
    owner.add_pet(Pet(name="Rex", species="dog", age=3))

    # Act: build a plan.
    plan = Scheduler().generate_daily_plan(owner, available_minutes=60)

    # Assert: still nothing to schedule.
    assert plan == []


# ---------------------------------------------------------------------------
# Edge case: a task that exactly fills the available time.
# ---------------------------------------------------------------------------
def test_daily_plan_includes_task_that_exactly_fills_time():
    """A task whose duration equals the budget should still be included."""

    # Arrange: one 30-minute task and exactly 30 minutes available.
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)
    rex.add_task(Task("Walk", "08:00", "daily", priority=5, duration_minutes=30))

    # Act: build a plan with a budget equal to the task's duration.
    plan = Scheduler().generate_daily_plan(owner, available_minutes=30)

    # Assert: the task fits exactly and is included.
    assert len(plan) == 1
    assert plan[0].description == "Walk"


# ---------------------------------------------------------------------------
# Edge case: a task that is too large for the remaining time.
# ---------------------------------------------------------------------------
def test_daily_plan_excludes_task_too_large_but_keeps_smaller_one():
    """A too-big task is skipped, but a smaller task that still fits is kept."""

    # Arrange: a big high-priority task and a small lower-priority task.
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)
    rex.add_task(Task("Long groom", "09:00", "weekly", priority=5, duration_minutes=60))
    rex.add_task(Task("Quick feed", "08:00", "daily", priority=3, duration_minutes=10))

    # Act: build a plan with only 30 minutes available.
    plan = Scheduler().generate_daily_plan(owner, available_minutes=30)

    # Assert: the 60-min task is skipped; the 10-min task still makes it in.
    descriptions = [task.description for task in plan]
    assert "Long groom" not in descriptions
    assert "Quick feed" in descriptions


# ---------------------------------------------------------------------------
# Edge case: two tasks with the same time but different dates.
# ---------------------------------------------------------------------------
def test_find_conflicts_same_time_different_dates_is_not_a_conflict():
    """Same time on different days should NOT be reported as a conflict."""

    # Arrange: two tasks at 08:00 but on different due dates.
    owner = Owner(name="Maya")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)
    today = date(2026, 7, 4)
    rex.add_task(
        Task("Walk", "08:00", "daily", priority=5, duration_minutes=30, due_date=today)
    )
    rex.add_task(
        Task(
            "Walk",
            "08:00",
            "daily",
            priority=5,
            duration_minutes=30,
            due_date=today + timedelta(days=1),
        )
    )

    # Act & Assert: different days means no clash.
    assert Scheduler().find_conflicts(owner) == []


# ---------------------------------------------------------------------------
# Requested test 1: Sorting Correctness
# Tasks given out of order should come back in chronological order.
# ---------------------------------------------------------------------------
def test_sort_by_time_returns_chronological_order():
    """sort_by_time should return tasks ordered by time, earliest first."""

    # Arrange: three tasks created deliberately out of chronological order.
    task_evening = Task("Evening play", "18:00", "daily", priority=2, duration_minutes=20)
    task_morning = Task("Morning walk", "08:00", "daily", priority=5, duration_minutes=30)
    task_midday = Task("Lunch feed", "12:00", "daily", priority=4, duration_minutes=10)
    unordered = [task_evening, task_morning, task_midday]

    # Act: sort the tasks by time.
    ordered = Scheduler().sort_by_time(unordered)

    # Assert: the tasks come back earliest-to-latest.
    assert ordered == [task_morning, task_midday, task_evening]
    assert [task.time for task in ordered] == ["08:00", "12:00", "18:00"]


# ---------------------------------------------------------------------------
# Requested test 2: Recurrence Logic
# Completing a daily task should create tomorrow's task on the pet.
# ---------------------------------------------------------------------------
def test_mark_complete_creates_next_day_task_on_pet():
    """mark_task_complete should complete the task and add the next day's copy."""

    # Arrange: a pet with one daily task on a fixed due date.
    pet = Pet(name="Luna", species="cat", age=2)
    today = date(2026, 7, 4)
    task = Task(
        description="Feed breakfast",
        time="07:30",
        frequency="daily",
        priority=5,
        duration_minutes=10,
        due_date=today,
    )
    pet.add_task(task)
    scheduler = Scheduler()

    # Act: complete the task through the scheduler.
    new_task = scheduler.mark_task_complete(pet, task)

    # Assert: the original task is now completed.
    assert task.completed is True

    # Assert: a new task was created for the following day.
    assert new_task is not None
    assert new_task.due_date == today + timedelta(days=1)
    assert new_task.completed is False

    # Assert: the new task was added to the pet.
    assert new_task in pet.get_tasks()
    assert len(pet.get_tasks()) == 2


# ---------------------------------------------------------------------------
# Requested test 3: Conflict Detection
# Two tasks at the same due date and time should produce one warning.
# ---------------------------------------------------------------------------
def test_find_conflicts_returns_one_warning_for_same_date_and_time():
    """find_conflicts should report exactly one warning for a same-slot clash."""

    # Arrange: an owner with one pet holding two tasks in the same time slot.
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)
    today = date(2026, 7, 4)
    rex.add_task(
        Task("Morning walk", "08:00", "daily", priority=5, duration_minutes=30, due_date=today)
    )
    rex.add_task(
        Task("Give medicine", "08:00", "daily", priority=4, duration_minutes=5, due_date=today)
    )

    # Act: look for conflicts.
    warnings = Scheduler().find_conflicts(owner)

    # Assert: exactly one conflict warning is returned.
    assert len(warnings) == 1


# ---------------------------------------------------------------------------
# Feature: find_next_available_slot returns the earliest free start time.
# ---------------------------------------------------------------------------
def test_next_slot_is_day_start_when_no_tasks():
    """With no tasks at all, the first available slot is the start of the day."""

    # Arrange: an owner with no pets (and therefore no tasks).
    owner = Owner(name="Sam")

    # Act: ask for a 30-minute slot.
    slot = Scheduler().find_next_available_slot(owner, duration_minutes=30)

    # Assert: the whole day is free, so we start at 08:00.
    assert slot == "08:00"


def test_next_slot_uses_gap_before_first_task():
    """A big enough gap before the first task should be used."""

    # Arrange: one task at 09:00, leaving an hour free before it.
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)
    rex.add_task(Task("Vet call", "09:00", "daily", priority=4, duration_minutes=20))

    # Act: a 30-minute task fits in the 08:00-09:00 gap.
    slot = Scheduler().find_next_available_slot(owner, duration_minutes=30)

    # Assert: it starts at the beginning of the day.
    assert slot == "08:00"


def test_next_slot_finds_gap_between_two_tasks():
    """A slot should be found in the free gap between two tasks."""

    # Arrange: a task at 08:00 (30 min, ends 08:30) and another at 10:00.
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)
    rex.add_task(Task("Morning walk", "08:00", "daily", priority=5, duration_minutes=30))
    rex.add_task(Task("Vet call", "10:00", "daily", priority=4, duration_minutes=20))

    # Act: a 30-minute task cannot start at 08:00, but fits after 08:30.
    slot = Scheduler().find_next_available_slot(owner, duration_minutes=30)

    # Assert: the gap starts right after the first task ends.
    assert slot == "08:30"


def test_next_slot_after_last_task_when_no_gap_fits():
    """When no gap is big enough, the slot is right after the final task."""

    # Arrange: back-to-back tasks with no room for a long new task.
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)
    rex.add_task(Task("Walk", "08:00", "daily", priority=5, duration_minutes=30))
    rex.add_task(Task("Feed", "08:30", "daily", priority=4, duration_minutes=15))

    # Act: a 60-minute task does not fit in any gap.
    slot = Scheduler().find_next_available_slot(owner, duration_minutes=60)

    # Assert: it starts after the last task ends (08:30 + 15 min = 08:45).
    assert slot == "08:45"


def test_next_slot_skips_gap_that_is_too_small():
    """A gap smaller than the requested duration should be skipped."""

    # Arrange: a task at 08:00 (30 min) and another at 08:45, leaving only a
    # 15-minute gap between them (08:30-08:45).
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)
    rex.add_task(Task("Walk", "08:00", "daily", priority=5, duration_minutes=30))
    rex.add_task(Task("Play", "08:45", "daily", priority=3, duration_minutes=30))

    # Act: a 20-minute task will not fit in the 15-minute gap.
    slot = Scheduler().find_next_available_slot(owner, duration_minutes=20)

    # Assert: it lands after the last task (08:45 + 30 min = 09:15).
    assert slot == "09:15"


# ---------------------------------------------------------------------------
# Data persistence: converting objects to dictionaries and back.
# ---------------------------------------------------------------------------
def test_task_to_dict_and_from_dict_round_trip():
    """A Task turned into a dict and back should be identical, with a real date."""

    # Arrange: a fully specified task on a known due date.
    task = Task(
        description="Feed breakfast",
        time="07:30",
        frequency="daily",
        priority=5,
        duration_minutes=10,
        completed=True,
        due_date=date(2026, 7, 4),
    )

    # Act: convert to a dict, then rebuild a task from that dict.
    data = task.to_dict()
    rebuilt = Task.from_dict(data)

    # Assert: the due_date was stored as a string but restored as a date.
    assert data["due_date"] == "2026-07-04"
    assert rebuilt.due_date == date(2026, 7, 4)

    # Assert: every field survived the round trip.
    assert rebuilt == task


def test_owner_to_dict_and_from_dict_round_trip():
    """An Owner with pets and tasks should survive a dict round trip."""

    # Arrange: an owner with one pet that has two tasks.
    owner = Owner(name="Maya")
    luna = Pet(name="Luna", species="cat", age=2)
    owner.add_pet(luna)
    luna.add_task(Task("Feed", "07:30", "daily", priority=5, duration_minutes=10))
    luna.add_task(Task("Play", "18:00", "weekly", priority=2, duration_minutes=20))

    # Act: convert to a dict, then rebuild an owner from that dict.
    rebuilt = Owner.from_dict(owner.to_dict())

    # Assert: the whole nested structure came back intact.
    assert rebuilt == owner


def test_save_and_load_from_json_round_trip(tmp_path):
    """Saving an owner to JSON and loading it back should preserve everything."""

    # Arrange: an owner with two pets and a mix of task fields.
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=2)
    owner.add_pet(rex)
    owner.add_pet(luna)
    rex.add_task(
        Task(
            "Morning walk",
            "08:00",
            "daily",
            priority=5,
            duration_minutes=30,
            due_date=date(2026, 7, 5),
        )
    )
    luna.add_task(
        Task(
            "Give medicine",
            "08:00",
            "daily",
            priority=4,
            duration_minutes=5,
            completed=True,
            due_date=date(2026, 7, 5),
        )
    )

    # Use a temporary file so the test never touches the real data.json.
    data_file = tmp_path / "data.json"

    # Act: save to JSON, then load it back into a new owner.
    owner.save_to_json(str(data_file))
    loaded = Owner.load_from_json(str(data_file))

    # Assert: the loaded owner matches the original, fields and all.
    assert loaded == owner

    # Assert (explicit): a saved due_date comes back as a real date object.
    loaded_task = loaded.get_pets()[0].get_tasks()[0]
    assert loaded_task.due_date == date(2026, 7, 5)


def test_load_from_json_returns_empty_owner_when_file_missing(tmp_path):
    """Loading from a file that does not exist should return a new empty owner."""

    # Arrange: a path to a file that has not been created.
    missing_file = tmp_path / "does_not_exist.json"

    # Act: try to load from the missing file.
    owner = Owner.load_from_json(str(missing_file))

    # Assert: we get a fresh Owner with no pets rather than an error.
    assert isinstance(owner, Owner)
    assert owner.get_pets() == []


# ---------------------------------------------------------------------------
# Advanced priority scheduling: named levels and priority-then-time sorting.
# ---------------------------------------------------------------------------
def test_priority_level_words_map_to_numbers():
    """The Low/Medium/High level words should convert to the right numbers."""

    # Act & Assert: each named level maps to its expected priority number.
    assert priority_from_level("Low") == 1
    assert priority_from_level("Medium") == 3
    assert priority_from_level("High") == 5

    # Assert: the lookup ignores capitalization.
    assert priority_from_level("high") == 5
    assert priority_from_level("HIGH") == 5


def test_priority_number_maps_back_to_word():
    """A priority number should convert back into its level word."""

    # Act & Assert: numbers turn back into the matching words.
    assert priority_to_label(1) == "Low"
    assert priority_to_label(3) == "Medium"
    assert priority_to_label(5) == "High"


def test_unknown_priority_level_raises_value_error():
    """An unrecognized level word should raise a clear ValueError."""

    # Act & Assert: an invalid word is rejected.
    import pytest

    with pytest.raises(ValueError):
        priority_from_level("urgent")


def test_sort_by_priority_then_time_orders_high_first():
    """High-priority tasks come first, regardless of their time of day."""

    # Arrange: a High task late in the day and a Low task early in the day.
    high_late = Task("Give medicine", "18:00", "daily", priority=5, duration_minutes=5)
    low_early = Task("Scoop litter", "08:00", "daily", priority=1, duration_minutes=10)

    # Act: sort by priority first, then time.
    ordered = Scheduler().sort_by_priority_then_time([low_early, high_late])

    # Assert: the High task wins even though it is later in the day.
    assert ordered == [high_late, low_early]


def test_sort_by_priority_then_time_breaks_ties_with_time():
    """Tasks sharing a priority should fall back to earliest-time-first."""

    # Arrange: three High tasks at different times, added out of order.
    late = Task("Evening walk", "18:00", "daily", priority=5, duration_minutes=30)
    early = Task("Morning walk", "08:00", "daily", priority=5, duration_minutes=30)
    midday = Task("Lunch feed", "12:00", "daily", priority=5, duration_minutes=10)

    # Act: sort by priority first, then time.
    ordered = Scheduler().sort_by_priority_then_time([late, early, midday])

    # Assert: same priority, so they come back in chronological order.
    assert [task.time for task in ordered] == ["08:00", "12:00", "18:00"]


def test_sort_by_priority_then_time_mixed_priorities_and_times():
    """The full rule: priority groups first, each group ordered by time."""

    # Arrange: a mix of priorities and times.
    high_late = Task("Medicine", "17:00", "daily", priority=5, duration_minutes=5)
    high_early = Task("Walk", "08:00", "daily", priority=5, duration_minutes=30)
    med = Task("Vet call", "09:00", "weekly", priority=3, duration_minutes=20)
    low = Task("Brush", "07:00", "weekly", priority=1, duration_minutes=15)

    # Act: sort by priority first, then time.
    ordered = Scheduler().sort_by_priority_then_time([low, high_late, med, high_early])

    # Assert: High group (earliest-first) -> Medium -> Low.
    assert ordered == [high_early, high_late, med, low]


def test_sort_by_priority_then_time_leaves_original_untouched():
    """The sort returns a new list and does not reorder the caller's list."""

    # Arrange: a list in a known order.
    first = Task("A", "09:00", "daily", priority=1, duration_minutes=5)
    second = Task("B", "08:00", "daily", priority=5, duration_minutes=5)
    original = [first, second]

    # Act: sort it.
    Scheduler().sort_by_priority_then_time(original)

    # Assert: the caller's list is unchanged.
    assert original == [first, second]


def test_daily_plan_orders_by_priority_then_time():
    """generate_daily_plan should order same-priority tasks by time."""

    # Arrange: two High tasks (added latest-first) plus a Medium task.
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)
    rex.add_task(Task("Evening meds", "18:00", "daily", priority=5, duration_minutes=5))
    rex.add_task(Task("Morning walk", "08:00", "daily", priority=5, duration_minutes=30))
    rex.add_task(Task("Vet call", "09:00", "weekly", priority=3, duration_minutes=20))

    # Act: build a plan with plenty of time.
    plan = Scheduler().generate_daily_plan(owner, available_minutes=120)

    # Assert: High tasks first (earliest-time-first within High), then Medium.
    assert [task.description for task in plan] == [
        "Morning walk",
        "Evening meds",
        "Vet call",
    ]


def test_task_get_info_shows_priority_word():
    """get_info() should show the priority as a word, not a raw number."""

    # Arrange: a High-priority task.
    task = Task("Walk", "08:00", "daily", priority=5, duration_minutes=30)

    # Act & Assert: the summary mentions "High".
    assert "priority High" in task.get_info()


# ---------------------------------------------------------------------------
# Output formatting: emojis, status icons, priority badges, and tables.
# ---------------------------------------------------------------------------
def test_task_emoji_matches_keywords():
    """Task descriptions with known keywords get the matching emoji."""

    # Act & Assert: each keyword maps to its emoji (case-insensitive).
    assert task_emoji("Morning walk") == "🚶"
    assert task_emoji("Feed breakfast") == "🍽️"
    assert task_emoji("Give medicine") == "💊"
    assert task_emoji("Vet appointment") == "🏥"
    assert task_emoji("Brush coat") == "🛁"
    assert task_emoji("Evening PLAY") == "🎾"


def test_task_emoji_falls_back_to_paw_print():
    """A description with no known keyword gets the default paw print."""

    # Act & Assert: nothing matched, so we get the fallback emoji.
    assert task_emoji("Do something unusual") == "🐾"


def test_status_icon_reflects_completion():
    """status_icon shows a check for done tasks and an empty box otherwise."""

    # Act & Assert: True -> check mark, False -> empty box.
    assert status_icon(True) == "✅"
    assert status_icon(False) == "⬜"


def test_priority_badge_plain_text_has_no_color_codes():
    """With color turned off, the badge is just the plain level word."""

    # Act & Assert: no ANSI escape codes, just the word.
    assert priority_badge(5, color=False) == "High"
    assert priority_badge(3, color=False) == "Medium"
    assert priority_badge(1, color=False) == "Low"


def test_priority_badge_colored_contains_the_word():
    """With color on, the badge still contains the level word."""

    # Act: build a colored badge.
    badge = priority_badge(5, color=True)

    # Assert: the word is present (wrapped in color codes).
    assert "High" in badge


def test_format_task_table_lists_tasks_and_headers():
    """format_task_table should include the column headers and every task."""

    # Arrange: two tasks with different types.
    tasks = [
        Task("Morning walk", "08:00", "daily", priority=5, duration_minutes=30),
        Task("Give medicine", "09:00", "daily", priority=3, duration_minutes=5),
    ]

    # Act: build the table without color so we can check the text plainly.
    table = format_task_table(tasks, color=False)

    # Assert: the headers and both task names appear in the table.
    assert "Time" in table
    assert "Priority" in table
    assert "Morning walk" in table
    assert "Give medicine" in table
    # And the type emojis are shown.
    assert "🚶" in table
    assert "💊" in table


def test_format_task_table_handles_no_tasks():
    """An empty task list should return a friendly message, not crash."""

    # Act & Assert: empty input gives a readable placeholder.
    assert format_task_table([]) == "  (no tasks to show)"


def test_format_plan_shows_total_time_and_tasks():
    """format_plan should include the tasks and a time-summary line."""

    # Arrange: a two-task plan.
    plan = [
        Task("Morning walk", "08:00", "daily", priority=5, duration_minutes=30),
        Task("Feed", "08:30", "daily", priority=4, duration_minutes=10),
    ]

    # Act: format the plan without color.
    text = format_plan(plan, available_minutes=60, color=False)

    # Assert: the summary reflects the total (30 + 10 = 40) of 60 minutes.
    assert "Total time planned: 40 of 60 minutes" in text
    assert "Morning walk" in text


def test_format_plan_handles_empty_plan():
    """An empty plan should return a clear 'nothing scheduled' message."""

    # Act: format an empty plan.
    text = format_plan([], available_minutes=60, color=False)

    # Assert: the message explains why nothing is shown.
    assert "Nothing scheduled" in text


# ---------------------------------------------------------------------------
# Rescheduling: overdue, not-done repeating tasks roll forward.
# ---------------------------------------------------------------------------
def test_reschedule_moves_overdue_daily_task_to_today():
    """An overdue, not-done daily task should jump to today."""

    # Arrange: a daily task due two days ago.
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)
    today = date(2026, 7, 5)
    task = Task(
        "Morning walk", "08:00", "daily",
        priority=5, duration_minutes=30, due_date=today - timedelta(days=2),
    )
    rex.add_task(task)

    # Act: reschedule overdue tasks as of `today`.
    moved = Scheduler().reschedule_overdue_tasks(owner, today=today)

    # Assert: the task moved to today, and the change was reported.
    assert task.due_date == today
    assert len(moved) == 1
    assert moved[0][0] is task
    assert moved[0][2] == today


def test_reschedule_weekly_task_preserves_weekday():
    """An overdue weekly task should advance in 7-day steps (same weekday)."""

    # Arrange: a weekly task due 10 days ago. 2026-06-25 is a Thursday.
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)
    original_due = date(2026, 6, 25)  # Thursday
    today = date(2026, 7, 5)          # a later Sunday
    task = Task(
        "Grooming", "10:00", "weekly",
        priority=3, duration_minutes=45, due_date=original_due,
    )
    rex.add_task(task)

    # Act: reschedule.
    Scheduler().reschedule_overdue_tasks(owner, today=today)

    # Assert: it landed on or after today...
    assert task.due_date >= today
    # ...and it is still a Thursday (same weekday as the original).
    assert task.due_date.weekday() == original_due.weekday()
    # Specifically the first Thursday on/after 2026-07-05 is 2026-07-09.
    assert task.due_date == date(2026, 7, 9)


def test_reschedule_leaves_completed_and_future_tasks_alone():
    """Completed tasks and tasks already due today/later are not moved."""

    # Arrange: a completed overdue task and a future task.
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)
    today = date(2026, 7, 5)

    done_overdue = Task(
        "Old walk", "08:00", "daily",
        priority=5, duration_minutes=30,
        completed=True, due_date=today - timedelta(days=3),
    )
    future = Task(
        "Future feed", "09:00", "daily",
        priority=4, duration_minutes=10, due_date=today + timedelta(days=1),
    )
    rex.add_task(done_overdue)
    rex.add_task(future)

    # Act: reschedule.
    moved = Scheduler().reschedule_overdue_tasks(owner, today=today)

    # Assert: nothing moved, and both dates are unchanged.
    assert moved == []
    assert done_overdue.due_date == today - timedelta(days=3)
    assert future.due_date == today + timedelta(days=1)


def test_reschedule_ignores_non_repeating_overdue_task():
    """A one-off (non daily/weekly) overdue task should be left in place."""

    # Arrange: a one-off task that is overdue but does not repeat.
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)
    today = date(2026, 7, 5)
    once = Task(
        "Adopt-day photo", "09:00", "once",
        priority=1, duration_minutes=5, due_date=today - timedelta(days=4),
    )
    rex.add_task(once)

    # Act: reschedule.
    moved = Scheduler().reschedule_overdue_tasks(owner, today=today)

    # Assert: one-off tasks are not rescheduled.
    assert moved == []
    assert once.due_date == today - timedelta(days=4)
