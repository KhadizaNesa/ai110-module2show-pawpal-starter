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
