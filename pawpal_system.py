"""PawPal+ logic layer.

This is the "backend" of the app: plain Python classes that model the
pet-care domain and decide what a daily plan should look like. There is no
UI code here on purpose — the user interface can import these classes and
use them without caring how they work inside.

Four main classes:
    Task      - one pet-care activity (e.g. "Morning walk").
    Pet       - a pet and the list of tasks it needs.
    Owner     - a person who looks after one or more pets.
    Scheduler - builds a daily plan from an owner's tasks.

Priority note: priority is an int where a HIGHER number means MORE important
(priority 5 is done before priority 1).
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional

# The daily plan starts at 8:00 AM. This is the earliest time the scheduler
# will suggest, and the value returned when there are no tasks yet.
DAY_START = "08:00"

# Priority is stored on a Task as a number where HIGHER means MORE important.
# To keep things friendly, users pick a word ("Low", "Medium", "High") and we
# translate it to a number with this table. These are the three named levels.
PRIORITY_LEVELS = {
    "Low": 1,
    "Medium": 3,
    "High": 5,
}

# The reverse lookup, so a number can be shown back to the user as a word.
PRIORITY_LABELS = {number: word for word, number in PRIORITY_LEVELS.items()}


def priority_from_level(level: str) -> int:
    """Turn a word like "High" into its priority number (e.g. 5).

    The lookup ignores capitalization, so "high", "High", and "HIGH" all work.
    Raises a clear error if the word is not one of the known levels.
    """
    try:
        return PRIORITY_LEVELS[level.capitalize()]
    except KeyError as exc:
        known = ", ".join(PRIORITY_LEVELS)
        raise ValueError(
            f"Unknown priority level '{level}'. Use one of: {known}."
        ) from exc


def priority_to_label(priority: int) -> str:
    """Turn a priority number back into a word (e.g. 5 -> "High").

    Numbers that are not one of the named levels fall back to showing the
    number itself, so nothing ever crashes on an unexpected value.
    """
    return PRIORITY_LABELS.get(priority, str(priority))


def _time_to_minutes(time_str: str) -> int:
    """Turn an "HH:MM" string into the number of minutes since midnight.

    Example: "08:30" -> 510  (8 * 60 + 30).
    """
    hours, minutes = time_str.split(":")
    return int(hours) * 60 + int(minutes)


def _minutes_to_time(total_minutes: int) -> str:
    """Turn a number of minutes since midnight back into an "HH:MM" string.

    Example: 510 -> "08:30". The hours and minutes are zero-padded to two
    digits so times always sort correctly as text.
    """
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}"


@dataclass
class Task:
    """One pet-care activity, such as a walk, a feeding, or giving medicine."""

    description: str          # what needs to be done, e.g. "Feed breakfast"
    time: str                 # when it should happen, e.g. "08:00" or "morning"
    frequency: str            # how often, e.g. "daily" or "weekly"
    priority: int             # higher number = more important
    duration_minutes: int     # how long the task takes
    completed: bool = False   # has it been done yet?
    # Which day this task is for. Defaults to today if not given.
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def create_next_occurrence(self) -> Optional["Task"]:
        """Return a not-completed copy for the next day/week, or None if it doesn't repeat."""
        if self.frequency == "daily":
            next_due = self.due_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due = self.due_date + timedelta(days=7)
        else:
            return None

        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            priority=self.priority,
            duration_minutes=self.duration_minutes,
            completed=False,
            due_date=next_due,
        )

    def mark_incomplete(self) -> None:
        """Mark this task as not done (e.g. to reset it for a new day)."""
        self.completed = False

    def priority_label(self) -> str:
        """Return this task's priority as a word ("Low", "Medium", or "High")."""
        return priority_to_label(self.priority)

    def get_info(self) -> str:
        """Return a readable one-line summary of the task."""
        status = "done" if self.completed else "not done"
        return (
            f"{self.description} at {self.time} "
            f"({self.frequency}, {self.duration_minutes} min, "
            f"priority {self.priority_label()}) - {status}"
        )

    def to_dict(self) -> dict:
        """Turn this task into a plain dictionary that JSON can store.

        ``due_date`` is a ``date`` object, which JSON cannot handle directly,
        so we save it as an "YYYY-MM-DD" string (e.g. "2026-07-05").
        """
        return {
            "description": self.description,
            "time": self.time,
            "frequency": self.frequency,
            "priority": self.priority,
            "duration_minutes": self.duration_minutes,
            "completed": self.completed,
            "due_date": self.due_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Build a Task back from a dictionary made by ``to_dict()``.

        The saved ``due_date`` is a string, so we turn it back into a real
        ``date`` object here.
        """
        return cls(
            description=data["description"],
            time=data["time"],
            frequency=data["frequency"],
            priority=data["priority"],
            duration_minutes=data["duration_minutes"],
            completed=data["completed"],
            due_date=date.fromisoformat(data["due_date"]),
        )


@dataclass
class Pet:
    """A pet and the list of care tasks that belong to it."""

    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)  # each pet starts with no tasks

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet (does nothing if it isn't there)."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self) -> List[Task]:
        """Return this pet's list of tasks."""
        return self.tasks

    def get_info(self) -> str:
        """Return a readable summary of the pet and how many tasks it has."""
        return (
            f"{self.name} ({self.species}, age {self.age}) "
            f"- {len(self.tasks)} task(s)"
        )

    def to_dict(self) -> dict:
        """Turn this pet (and all of its tasks) into a plain dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Build a Pet back from a dictionary, rebuilding each of its tasks."""
        return cls(
            name=data["name"],
            species=data["species"],
            age=data["age"],
            tasks=[Task.from_dict(task_data) for task_data in data["tasks"]],
        )


@dataclass
class Owner:
    """A person who looks after one or more pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)  # each owner starts with no pets

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner (does nothing if it isn't there)."""
        if pet in self.pets:
            self.pets.remove(pet)

    def get_pets(self) -> List[Pet]:
        """Return the owner's list of pets."""
        return self.pets

    def get_all_tasks(self) -> List[Task]:
        """Collect the tasks from every pet into one combined list."""
        all_tasks: List[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def to_dict(self) -> dict:
        """Turn this owner (and all of its pets and tasks) into a dictionary."""
        return {
            "name": self.name,
            "pets": [pet.to_dict() for pet in self.pets],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Build an Owner back from a dictionary, rebuilding all of its pets."""
        return cls(
            name=data["name"],
            pets=[Pet.from_dict(pet_data) for pet_data in data["pets"]],
        )

    def save_to_json(self, filename: str = "data.json") -> None:
        """Save this owner (with every pet and task) to a JSON file.

        The whole owner is first turned into nested dictionaries with
        ``to_dict()``, then written out as readable, indented JSON.
        """
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=2)

    @classmethod
    def load_from_json(cls, filename: str = "data.json") -> "Owner":
        """Load an owner back from a JSON file.

        If the file does not exist yet (for example on the very first run),
        return a fresh, empty owner instead of raising an error.
        """
        if not os.path.exists(filename):
            return cls(name="")

        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        return cls.from_dict(data)


class Scheduler:
    """Looks across all of an owner's pets and organizes their tasks.

    The Scheduler does not store any data itself. It is given an Owner and
    works out which tasks to do and in what order.
    """

    def get_tasks_from_owner(self, owner: Owner) -> List[Task]:
        """Get every task from every pet the owner has."""
        return owner.get_all_tasks()

    def sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return the tasks ordered from most important to least important.

        A higher priority number comes first. `sorted` does not change the
        original list, so the caller's list is left untouched.
        """
        return sorted(tasks, key=lambda task: task.priority, reverse=True)

    def sort_by_priority_then_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered by priority first (High to Low), then by time.

        This is the "advanced" ordering: the most important tasks come first,
        and when two tasks share the same priority the earlier time wins. The
        sort key is a tuple ``(-priority, time)`` -- Python compares tuples
        left-to-right, so it settles priority before it ever looks at the time.
        The minus sign flips the priority so a HIGHER number sorts first while
        the time still sorts earliest-first.

        ``sorted`` returns a new list, so the caller's list is left untouched.
        """
        return sorted(tasks, key=lambda task: (-task.priority, task.time))

    def get_incomplete_tasks(self, tasks: List[Task]) -> List[Task]:
        """Return only the tasks that have not been completed yet."""
        return [task for task in tasks if not task.completed]

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return a new list of the tasks ordered by their "HH:MM" time, earliest first."""
        return sorted(tasks, key=lambda task: task.time)

    def filter_by_completion(self, tasks: List[Task], completed: bool) -> List[Task]:
        """Return only the tasks whose completed flag matches the given value (True or False)."""
        return [task for task in tasks if task.completed == completed]

    def filter_by_pet_name(self, owner: Owner, pet_name: str) -> List[Task]:
        """Return the tasks that belong to one pet, found by its name.

        If no pet has that name, return an empty list.
        """
        for pet in owner.get_pets():
            if pet.name == pet_name:
                return pet.get_tasks()
        return []

    def find_conflicts(self, owner: Owner) -> List[str]:
        """Return warning strings for tasks on the same day and time (empty list if none)."""
        # Group task labels by the (day, time) slot they occupy.
        # defaultdict(list) starts each new slot as an empty list for us, so we
        # can append right away without checking whether the slot exists yet.
        slots: dict[tuple[date, str], list[str]] = defaultdict(list)
        for pet in owner.get_pets():
            for task in pet.get_tasks():
                key = (task.due_date, task.time)
                label = f"{task.description} ({pet.name})"
                slots[key].append(label)

        # Any slot holding more than one task is a conflict worth warning about.
        warnings: List[str] = []
        for (due_date, time), labels in slots.items():
            if len(labels) > 1:
                clashing = " and ".join(labels)
                warnings.append(
                    f"Conflict on {due_date} at {time}: {clashing}"
                )
        return warnings

    def find_next_available_slot(self, owner: Owner, duration_minutes: int) -> str:
        """Find the earliest "HH:MM" start time where a task would fit.

        The day is treated as starting at DAY_START ("08:00"). The scheduler
        looks at every task the owner has, puts them in time order, and walks
        through the day looking for the first free gap big enough to hold a
        task of ``duration_minutes``.

        Rules:
            - If the owner has no tasks, return "08:00".
            - If a gap between the start of the day and the tasks (or between
              two tasks) is large enough, return the start of that gap.
            - If no gap is large enough, return the time right after the very
              last task finishes.

        Args:
            owner: The owner whose tasks fill up the day.
            duration_minutes: How long the new task would take.

        Returns:
            The earliest start time, as an "HH:MM" string.
        """
        tasks = owner.get_all_tasks()

        # No tasks at all means the whole day is free, so start at the beginning.
        if not tasks:
            return DAY_START

        # Put the tasks in time order so we can scan them from earliest to latest.
        ordered = self.sort_by_time(tasks)

        # "cursor" is the earliest minute of the day that is still free. It
        # starts at the beginning of the day and moves forward past each task.
        cursor = _time_to_minutes(DAY_START)

        for task in ordered:
            task_start = _time_to_minutes(task.time)

            # How much free space is there between the cursor and this task?
            gap = task_start - cursor
            if gap >= duration_minutes:
                # The new task fits in this gap, so start it at the cursor.
                return _minutes_to_time(cursor)

            # Not enough room here. Move the cursor to the end of this task.
            # max(...) guards against tasks that start before the cursor
            # (for example two tasks that overlap) so the cursor only moves
            # forward, never backward.
            task_end = task_start + task.duration_minutes
            cursor = max(cursor, task_end)

        # No gap was big enough, so the earliest slot is after the last task.
        return _minutes_to_time(cursor)

    def mark_task_complete(self, pet: Pet, task: Task) -> Optional[Task]:
        """Mark the task done, add its next occurrence to the pet, and return that new task (or None)."""
        task.mark_complete()
        next_task = task.create_next_occurrence()
        if next_task is not None:
            pet.add_task(next_task)
        return next_task

    def reschedule_overdue_tasks(
        self, owner: Owner, today: Optional[date] = None
    ) -> List[tuple]:
        """Roll every overdue, not-done repeating task forward to its next date.

        A task is "overdue" when it is not completed and its ``due_date`` is
        before ``today``. This happens when an owner misses a day: yesterday's
        unfinished walk should move forward instead of being lost.

        How each task moves depends on its frequency:
            - ``daily``  -> jumps straight to ``today`` (it should happen again
              every day, so the soonest valid day is today).
            - ``weekly`` -> advances in whole 7-day steps until it lands on or
              after ``today``. Stepping by 7 keeps the task on the SAME weekday
              it was booked for (a Monday grooming stays on a Monday), which a
              naive "just set it to today" approach would quietly break.

        Completed tasks and non-repeating tasks (anything that is not daily or
        weekly) are left untouched.

        Args:
            owner: The owner whose pets' tasks may need rescheduling.
            today: The day to catch up to. Defaults to the real today.

        Returns:
            A list of ``(task, old_date, new_date)`` tuples, one for every task
            that was actually moved. Tasks already on or after ``today`` are not
            included.
        """
        if today is None:
            today = date.today()

        moved: List[tuple] = []
        for pet in owner.get_pets():
            for task in pet.get_tasks():
                # Skip anything that is done or not overdue.
                if task.completed or task.due_date >= today:
                    continue

                old_date = task.due_date
                if task.frequency == "daily":
                    new_date = today
                elif task.frequency == "weekly":
                    # Step forward a week at a time so the weekday is preserved.
                    new_date = task.due_date
                    while new_date < today:
                        new_date += timedelta(days=7)
                else:
                    # One-off tasks do not repeat, so we leave them where they are.
                    continue

                task.due_date = new_date
                moved.append((task, old_date, new_date))

        return moved

    def generate_daily_plan(self, owner: Owner, available_minutes: int) -> List[Task]:
        """Build today's plan for an owner.

        Steps:
            1. Gather every task from the owner's pets.
            2. Keep only the tasks that still need doing.
            3. Order them by priority first (High to Low), then by time so that
               same-priority tasks run earliest-first.
            4. Add tasks one by one until the time budget runs out.

        Returns the chosen tasks, in the order they should be done.
        """
        all_tasks = self.get_tasks_from_owner(owner)
        incomplete = self.get_incomplete_tasks(all_tasks)
        ordered = self.sort_by_priority_then_time(incomplete)

        plan: List[Task] = []
        minutes_used = 0
        for task in ordered:
            # Only add the task if it still fits in the remaining time.
            if minutes_used + task.duration_minutes <= available_minutes:
                plan.append(task)
                minutes_used += task.duration_minutes
        return plan


# A small demo so you can run this file directly and see it work:
#     python pawpal_system.py
if __name__ == "__main__":
    # Build an owner with one pet and a few tasks. The tasks are added out of
    # both priority and time order on purpose, so the scheduling can show off.
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)

    # Note the mix: a High task late in the day (18:00) and a Low task early
    # (08:15). Sorting by time alone would put the Low task first.
    rex.add_task(
        Task("Give medicine", "18:00", "daily",
             priority=priority_from_level("High"), duration_minutes=5)
    )
    rex.add_task(
        Task("Scoop litter", "08:15", "daily",
             priority=priority_from_level("Low"), duration_minutes=10)
    )
    rex.add_task(
        Task("Morning walk", "08:00", "daily",
             priority=priority_from_level("High"), duration_minutes=30)
    )
    rex.add_task(
        Task("Vet call", "10:00", "weekly",
             priority=priority_from_level("Medium"), duration_minutes=20)
    )

    scheduler = Scheduler()

    # First, show what plain time sorting would do (the "before").
    print("Sorted by time only (old behavior):")
    for task in scheduler.sort_by_time(rex.get_tasks()):
        print(f"  {task.time}  {task.description:<14} [{task.priority_label()}]")

    print()

    # Now the advanced ordering: priority first, then time (the "after").
    print("Sorted by priority, then time (advanced scheduling):")
    for task in scheduler.sort_by_priority_then_time(rex.get_tasks()):
        print(f"  {task.time}  {task.description:<14} [{task.priority_label()}]")

    print()

    # And the full daily plan, which now uses priority-then-time ordering.
    plan = scheduler.generate_daily_plan(owner, available_minutes=60)
    print(f"Daily plan for {owner.name} (60 minutes available):")
    for task in plan:
        print(f"  - {task.get_info()}")
