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

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


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

    def get_info(self) -> str:
        """Return a readable one-line summary of the task."""
        status = "done" if self.completed else "not done"
        return (
            f"{self.description} at {self.time} "
            f"({self.frequency}, {self.duration_minutes} min, "
            f"priority {self.priority}) - {status}"
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

    def mark_task_complete(self, pet: Pet, task: Task) -> Optional[Task]:
        """Mark the task done, add its next occurrence to the pet, and return that new task (or None)."""
        task.mark_complete()
        next_task = task.create_next_occurrence()
        if next_task is not None:
            pet.add_task(next_task)
        return next_task

    def generate_daily_plan(self, owner: Owner, available_minutes: int) -> List[Task]:
        """Build today's plan for an owner.

        Steps:
            1. Gather every task from the owner's pets.
            2. Keep only the tasks that still need doing.
            3. Put the most important tasks first.
            4. Add tasks one by one until the time budget runs out.

        Returns the chosen tasks, in the order they should be done.
        """
        all_tasks = self.get_tasks_from_owner(owner)
        incomplete = self.get_incomplete_tasks(all_tasks)
        ordered = self.sort_tasks_by_priority(incomplete)

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
    # Build an owner with one pet and a few tasks.
    owner = Owner(name="Sam")
    rex = Pet(name="Rex", species="dog", age=3)
    owner.add_pet(rex)

    rex.add_task(Task("Morning walk", "08:00", "daily", priority=5, duration_minutes=30))
    rex.add_task(Task("Feed breakfast", "08:30", "daily", priority=5, duration_minutes=10))
    rex.add_task(Task("Vet call", "10:00", "weekly", priority=4, duration_minutes=20))
    rex.add_task(Task("Brush coat", "18:00", "weekly", priority=2, duration_minutes=15))

    scheduler = Scheduler()
    plan = scheduler.generate_daily_plan(owner, available_minutes=60)

    print(f"Daily plan for {owner.name} (60 minutes available):")
    for task in plan:
        print(f"  - {task.get_info()}")
