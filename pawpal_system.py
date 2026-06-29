"""PawPal logic layer.

Backend classes for building a daily pet-care plan. The data objects
(Pet, CareTask, Owner, CarePlan) are dataclasses; PlanGenerator holds the
scheduling logic that turns a list of tasks into a time-bounded CarePlan.

This mirrors the UML class diagram in diagrams/uml.mmd.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Pet:
    """An animal the owner cares for."""

    name: str
    species: str
    age: int

    def get_info(self) -> str:
        return f"{self.name} ({self.species}, age {self.age})"


@dataclass
class CareTask:
    """A single unit of care work (feeding, walk, meds, etc.)."""

    title: str
    category: str
    priority: int  # lower number = higher priority
    duration_minutes: int
    preferred_time: str = ""
    is_complete: bool = False

    def mark_complete(self) -> None:
        self.is_complete = True

    def get_duration(self) -> int:
        return self.duration_minutes


@dataclass
class Owner:
    """The person responsible for the pets and their care tasks."""

    name: str
    available_minutes: int
    preferences: str = ""
    pets: List[Pet] = field(default_factory=list)
    tasks: List[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        self.tasks.append(task)

    def remove_task(self, task: CareTask) -> None:
        if task in self.tasks:
            self.tasks.remove(task)

    def set_preferences(self, prefs: str) -> None:
        self.preferences = prefs


@dataclass
class CarePlan:
    """A scheduled set of care tasks for a given day."""

    date: str
    total_minutes: int = 0
    scheduled_tasks: List[CareTask] = field(default_factory=list)
    explanation: str = ""

    def add_task(self, task: CareTask) -> None:
        self.scheduled_tasks.append(task)
        self.total_minutes += task.get_duration()

    def generate_plan(self, tasks: List[CareTask], available_time: int) -> None:
        """Fill the plan with as many high-priority tasks as fit in the time budget."""
        self.scheduled_tasks = []
        self.total_minutes = 0
        ordered = sorted(tasks, key=lambda t: t.priority)
        skipped: List[CareTask] = []
        for task in ordered:
            if self.total_minutes + task.get_duration() <= available_time:
                self.add_task(task)
            else:
                skipped.append(task)
        self.explanation = self._build_explanation(available_time, skipped)

    def _build_explanation(self, available_time: int, skipped: List[CareTask]) -> str:
        lines = [
            f"Scheduled {len(self.scheduled_tasks)} task(s) using "
            f"{self.total_minutes} of {available_time} available minutes, "
            "prioritizing the most important tasks first."
        ]
        if skipped:
            names = ", ".join(t.title for t in skipped)
            lines.append(f"Skipped (not enough time): {names}.")
        return " ".join(lines)

    def explain_plan(self) -> str:
        """Explain why this daily plan was chosen."""
        return self.explanation

    def get_summary(self) -> str:
        if not self.scheduled_tasks:
            return f"{self.date}: no tasks scheduled."
        items = ", ".join(
            f"{t.title} ({t.get_duration()}m)" for t in self.scheduled_tasks
        )
        return f"{self.date}: {items} — {self.total_minutes} min total."


class PlanGenerator:
    """Builds a CarePlan from an owner's tasks and available time."""

    @staticmethod
    def sort_by_priority(tasks: List[CareTask]) -> List[CareTask]:
        return sorted(tasks, key=lambda t: t.priority)

    @staticmethod
    def fit_to_time(tasks: List[CareTask], available_time: int) -> List[CareTask]:
        fitted: List[CareTask] = []
        used = 0
        for task in PlanGenerator.sort_by_priority(tasks):
            if used + task.get_duration() <= available_time:
                fitted.append(task)
                used += task.get_duration()
        return fitted

    def build(self, owner: Owner, pet: Pet, tasks: List[CareTask], date: str = "") -> CarePlan:
        plan = CarePlan(date=date)
        plan.generate_plan(tasks, owner.available_minutes)
        return plan


if __name__ == "__main__":
    owner = Owner(name="Sam", available_minutes=60, preferences="mornings")
    pet = Pet(name="Rex", species="dog", age=3)
    owner.pets.append(pet)

    owner.add_task(CareTask("Morning walk", "exercise", priority=1, duration_minutes=30))
    owner.add_task(CareTask("Feed breakfast", "feeding", priority=1, duration_minutes=10))
    owner.add_task(CareTask("Brush coat", "grooming", priority=3, duration_minutes=15))
    owner.add_task(CareTask("Vet call", "health", priority=2, duration_minutes=20))

    plan = PlanGenerator().build(owner, pet, owner.tasks, date="2026-06-29")
    print(plan.get_summary())
    print(plan.explain_plan())
