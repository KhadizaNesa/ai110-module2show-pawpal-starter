"""PawPal+ demo.

This file shows how to USE the logic layer in pawpal_system.py.
It builds an owner with a couple of pets, gives them some tasks, and then
asks the Scheduler to build a daily plan that fits into the available time.

Run it with:
    python main.py
"""

# Bring in the classes we need from the logic layer.
from pawpal_system import Owner, Pet, Task, Scheduler, priority_from_level

# Bring in the presentation helpers (colors, emojis, and tables).
from formatting import (
    format_heading,
    format_plan,
    format_task_table,
    status_icon,
    task_emoji,
)


def main() -> None:
    # 1. Create one owner.
    owner = Owner(name="Maya")

    # 2. Create at least two pets.
    luna = Pet(name="Luna", species="cat", age=2)
    buddy = Pet(name="Buddy", species="dog", age=4)

    # 3. Add the pets to the owner.
    owner.add_pet(luna)
    owner.add_pet(buddy)

    # 4. Add at least three tasks to the pets.
    #    Notice the times are added OUT OF ORDER on purpose, so we can see
    #    what sorting by time does later.
    #    Remember: a HIGHER priority number means MORE important. Here we use
    #    the named levels ("Low"/"Medium"/"High") so the output shows words.
    luna.add_task(Task("Clean litter box", "12:00", "daily",
                       priority=priority_from_level("Medium"), duration_minutes=15))
    luna.add_task(Task("Feed breakfast", "07:30", "daily",
                       priority=priority_from_level("High"), duration_minutes=10))

    buddy.add_task(Task("Evening play", "18:00", "daily",
                        priority=priority_from_level("Low"), duration_minutes=20))
    buddy.add_task(Task("Morning walk", "08:00", "daily",
                        priority=priority_from_level("High"), duration_minutes=30))
    buddy.add_task(Task("Vet appointment", "10:30", "weekly",
                        priority=priority_from_level("Medium"), duration_minutes=25))

    # Give Luna a task at 08:00 too -- the SAME time as Buddy's morning walk.
    # This is on purpose so the conflict detector has something to warn about.
    luna.add_task(Task("Give medicine", "08:00", "daily",
                       priority=priority_from_level("High"), duration_minutes=5))

    # Mark one task as done so the "incomplete only" filter has something to hide.
    luna.get_tasks()[0].mark_complete()  # Luna's "Clean litter box" is finished

    # 5. Create a scheduler.
    scheduler = Scheduler()

    # 5b. Show off the sorting/filtering methods with nicely formatted tables.
    #     A small helper so we don't repeat the heading + table printing.
    def print_tasks(title: str, tasks) -> None:
        print("\n" + format_heading(title))
        print(format_task_table(tasks))

    all_tasks = owner.get_all_tasks()

    # Sorted by priority then time: the advanced scheduling order.
    print_tasks(
        "All tasks (by priority, then time):",
        scheduler.sort_by_priority_then_time(all_tasks),
    )

    # Incomplete only: hides anything already marked done.
    print_tasks(
        "Incomplete tasks only:",
        scheduler.filter_by_completion(all_tasks, completed=False),
    )

    # Tasks for one pet, found by name.
    print_tasks(
        "Tasks for Buddy:",
        scheduler.filter_by_pet_name(owner, "Buddy"),
    )

    # 5c. Automate a recurring task.
    #     "Feed breakfast" is a DAILY task, so completing it today should
    #     automatically schedule the same task for tomorrow.
    print("\n" + format_heading("🔁 Recurring task demo:"))
    feed_breakfast = luna.get_tasks()[1]  # Luna's daily "Feed breakfast"
    new_task = scheduler.mark_task_complete(luna, feed_breakfast)

    icon = f"{status_icon(feed_breakfast.completed)} {task_emoji(feed_breakfast.description)}"
    print(f"  Completed: {icon} {feed_breakfast.get_info()}")
    print(f"  (was due {feed_breakfast.due_date})")
    if new_task is not None:
        next_icon = f"{status_icon(new_task.completed)} {task_emoji(new_task.description)}"
        print(f"  Next up:   {next_icon} {new_task.get_info()}")
        print(f"  (now due {new_task.due_date})")
    else:
        print("  This task does not repeat.")

    # 5d. Check for scheduling conflicts (same day + same time).
    print("\n" + format_heading("⚠️  Conflict check:"))
    conflicts = scheduler.find_conflicts(owner)
    if conflicts:
        for warning in conflicts:
            print(f"  ⚠️  {warning}")
    else:
        print("  ✅ No conflicts found.")

    # 6. Generate a daily plan that fits into the time we have today.
    available_minutes = 60
    plan = scheduler.generate_daily_plan(owner, available_minutes=available_minutes)

    # 7. Print a clean, readable schedule (not raw Python objects).
    print()
    print(format_heading(f"📅 Today's Schedule for {owner.name}"))
    print(format_heading(f"(Time available: {available_minutes} minutes)"))

    # Show which pets the owner is caring for.
    print("\n" + format_heading("🐾 Pets:"))
    for pet in owner.get_pets():
        print(f"  - {pet.get_info()}")

    # Show the planned tasks, ordered by priority then time, as a table.
    print("\n" + format_heading("✨ Planned tasks:"))
    print(format_plan(plan, available_minutes))


# Only run the demo when this file is executed directly.
if __name__ == "__main__":
    main()
