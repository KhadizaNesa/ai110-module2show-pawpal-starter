"""Beginner-friendly unit tests for the PawPal+ system.

Run them from the project root with:
    pytest

Each test follows a simple "Arrange, Act, Assert" pattern:
    1. Arrange - set up the objects we need.
    2. Act     - do the thing we want to test.
    3. Assert  - check that the result is what we expect.
"""

from datetime import date, timedelta

from pawpal_system import Task, Pet, Owner, Scheduler


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
