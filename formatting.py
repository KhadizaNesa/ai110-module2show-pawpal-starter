"""PawPal+ presentation layer.

This module turns the plain data from ``pawpal_system.py`` into friendly,
colorful CLI output. Keeping it separate means the logic layer stays free of
any printing or formatting code.

Two outside libraries do the heavy lifting:
    tabulate  - draws neat, aligned text tables.
    colorama  - adds ANSI colors that also work on Windows terminals.

Everything here is beginner-friendly: small helper functions with clear names.
"""

from __future__ import annotations

from typing import List

from colorama import Fore, Style, init as colorama_init
from tabulate import tabulate

from pawpal_system import Task, priority_to_label

# Turn colorama on. ``autoreset=True`` means every colored string goes back to
# normal on its own, so we never have to remember to reset the color by hand.
colorama_init(autoreset=True)


# An emoji for each kind of task. We look at the words in the task description
# and pick the first keyword that matches. If nothing matches we fall back to
# the paw print, so every task still gets an icon.
TASK_EMOJIS = {
    "walk": "🚶",
    "feed": "🍽️",
    "breakfast": "🍽️",
    "dinner": "🍽️",
    "meal": "🍽️",
    "water": "💧",
    "medicine": "💊",
    "med": "💊",
    "pill": "💊",
    "vet": "🏥",
    "groom": "🛁",
    "brush": "🛁",
    "bath": "🛁",
    "wash": "🛁",
    "play": "🎾",
    "fetch": "🎾",
    "litter": "🧹",
    "clean": "🧹",
    "train": "🎓",
    "sleep": "😴",
    "nap": "😴",
    "photo": "📸",
}

DEFAULT_EMOJI = "🐾"  # used when no keyword matches


def task_emoji(description: str) -> str:
    """Pick an emoji for a task based on words in its description.

    The check is case-insensitive, so "Morning Walk" and "morning walk" both
    return the walking emoji. If no keyword is found, a paw print is returned.
    """
    lowered = description.lower()
    for keyword, emoji in TASK_EMOJIS.items():
        if keyword in lowered:
            return emoji
    return DEFAULT_EMOJI


def status_icon(completed: bool) -> str:
    """Return a check mark for done tasks and an empty box for not-done ones."""
    return "✅" if completed else "⬜"


def priority_badge(priority: int, color: bool = True) -> str:
    """Return the priority as a word, optionally color-coded.

    High is shown in red, Medium in yellow, and Low in green. Passing
    ``color=False`` returns just the plain word (handy for tests and for
    places where colors are not wanted).
    """
    label = priority_to_label(priority)
    if not color:
        return label

    colors = {
        "High": Fore.RED,
        "Medium": Fore.YELLOW,
        "Low": Fore.GREEN,
    }
    tint = colors.get(label, "")
    return f"{tint}{label}{Style.RESET_ALL}"


def status_text(completed: bool, color: bool = True) -> str:
    """Return a colored 'done'/'not done' label (green when done, grey when not)."""
    if completed:
        text = "done"
        tint = Fore.GREEN if color else ""
    else:
        text = "not done"
        tint = Fore.LIGHTBLACK_EX if color else ""
    if not color:
        return text
    return f"{tint}{text}{Style.RESET_ALL}"


def format_task_row(task: Task, color: bool = True) -> list:
    """Build one table row (a list of cells) for a single task."""
    return [
        f"{status_icon(task.completed)} {task_emoji(task.description)}",
        task.time,
        task.description,
        task.frequency,
        priority_badge(task.priority, color=color),
        f"{task.duration_minutes} min",
        status_text(task.completed, color=color),
    ]


def format_task_table(tasks: List[Task], color: bool = True) -> str:
    """Return a structured, aligned table of tasks built with ``tabulate``.

    Columns: an icon (status + type emoji), time, task, frequency, priority,
    duration, and status. Returns a friendly message if there are no tasks.
    """
    if not tasks:
        return "  (no tasks to show)"

    headers = ["", "Time", "Task", "Freq", "Priority", "Duration", "Status"]
    rows = [format_task_row(task, color=color) for task in tasks]
    return tabulate(rows, headers=headers, tablefmt="rounded_grid")


def format_heading(text: str, color: bool = True) -> str:
    """Return a bold, cyan section heading (plain text when color is off)."""
    if not color:
        return text
    return f"{Style.BRIGHT}{Fore.CYAN}{text}{Style.RESET_ALL}"


def format_plan(plan: List[Task], available_minutes: int, color: bool = True) -> str:
    """Return the full daily-plan block: a table plus a time summary line.

    The summary turns green if the plan fits inside the available minutes and
    yellow if it is completely full (uses every minute or more).
    """
    if not plan:
        return "  (Nothing scheduled — no time available or no tasks to do.)"

    table = format_task_table(plan, color=color)

    total = sum(task.duration_minutes for task in plan)
    summary = f"Total time planned: {total} of {available_minutes} minutes"
    if color:
        tint = Fore.YELLOW if total >= available_minutes else Fore.GREEN
        summary = f"{tint}{summary}{Style.RESET_ALL}"

    return f"{table}\n\n{summary}"
