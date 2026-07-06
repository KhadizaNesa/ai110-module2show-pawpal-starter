import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler, priority_from_level
from formatting import task_emoji, status_icon

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# One Scheduler used everywhere below. It holds no state of its own, so a
# single shared instance is fine for sorting, filtering, and conflict checks.
scheduler = Scheduler()

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")

# Load any saved owner (with its pets and tasks) from data.json the first time
# the app runs. If data.json does not exist yet, load_from_json() returns a
# fresh, empty Owner. We keep the result in session_state so it survives reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner.load_from_json()
owner = st.session_state.owner

# Pre-fill the name box with whatever was loaded (falls back to "Jordan").
owner_name = st.text_input("Owner name", value=owner.name or "Jordan")
owner.name = owner_name  # keep the stored owner's name in sync with the input

# Let the user save the current owner, pets, and tasks back to data.json.
if st.button("💾 Save data"):
    owner.save_to_json()
    st.success("Saved pets and tasks to data.json.")

st.divider()

# --- Add a Pet ----------------------------------------------------------
st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
age = st.number_input("Age (years)", min_value=0, max_value=50, value=1)

if st.button("Add pet"):
    # Owner.add_pet() is the method that stores the new Pet on the owner.
    owner.add_pet(Pet(name=pet_name, species=species, age=int(age)))
    st.success(f"Added {pet_name} to {owner.name}.")

# Show the pets the owner currently has (read back from the Owner object).
if owner.get_pets():
    st.write("Current pets:")
    for pet in owner.get_pets():
        st.write("- " + pet.get_info())
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add a Task to a Pet ------------------------------------------------
st.subheader("Add a Task")

if not owner.get_pets():
    st.info("Add a pet first, then you can give it tasks.")
else:
    pet_names = [pet.name for pet in owner.get_pets()]
    chosen_pet_name = st.selectbox("Which pet is this task for?", pet_names)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority_label = st.selectbox("Priority", ["Low", "Medium", "High"], index=2)

    task_time = st.text_input("Time", value="08:00")
    frequency = st.selectbox("Frequency", ["daily", "weekly"])

    if st.button("Add task"):
        # Find the Pet object the user picked...
        chosen_pet = next(p for p in owner.get_pets() if p.name == chosen_pet_name)
        # ...then Pet.add_task() attaches the new Task to it. The Task stores
        # priority as a number (higher = more important), so translate the
        # chosen word ("High") into its number with priority_from_level().
        chosen_pet.add_task(
            Task(
                description=task_title,
                time=task_time,
                frequency=frequency,
                priority=priority_from_level(priority_label),
                duration_minutes=int(duration),
            )
        )
        st.success(f"Added '{task_title}' to {chosen_pet_name}.")

    # Show tasks across the owner's pets, in chronological order.
    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("Current tasks:")

        # --- Filter controls ---------------------------------------------
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            pet_filter = st.selectbox("Filter by pet", ["All pets"] + pet_names)
        with fcol2:
            status_filter = st.selectbox(
                "Filter by status", ["All", "Not done", "Done"]
            )

        # Narrow to one pet's tasks if a specific pet is chosen.
        if pet_filter == "All pets":
            tasks_to_show = all_tasks
        else:
            tasks_to_show = scheduler.filter_by_pet_name(owner, pet_filter)

        # Narrow by completion status if one is chosen.
        if status_filter == "Done":
            tasks_to_show = scheduler.filter_by_completion(tasks_to_show, True)
        elif status_filter == "Not done":
            tasks_to_show = scheduler.filter_by_completion(tasks_to_show, False)

        # Put whatever is left in chronological (earliest-time-first) order.
        tasks_to_show = scheduler.sort_by_time(tasks_to_show)

        # Warn about any tasks that clash on the same day and time.
        conflicts = scheduler.find_conflicts(owner)
        for conflict in conflicts:
            st.warning(conflict)

        if tasks_to_show:
            st.dataframe(
                [
                    {
                        "": f"{status_icon(task.completed)} {task_emoji(task.description)}",
                        "Time": task.time,
                        "Task": task.description,
                        "Frequency": task.frequency,
                        "Priority": task.priority_label(),
                        "Duration (min)": task.duration_minutes,
                        "Status": "✅ done" if task.completed else "⬜ not done",
                    }
                    for task in tasks_to_show
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No tasks match the current filters.")
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# --- Build the daily schedule -------------------------------------------
st.subheader("Build Schedule")
available_minutes = st.number_input(
    "Minutes available today", min_value=1, max_value=1440, value=60
)

if st.button("Generate schedule"):
    # Scheduler.generate_daily_plan() reads the owner's pets/tasks and
    # returns the tasks to do today, most important first.
    plan = scheduler.generate_daily_plan(owner, available_minutes=int(available_minutes))
    if plan:
        st.write(f"Daily plan for {owner.name} ({int(available_minutes)} minutes):")
        for task in plan:
            st.write("- " + task.get_info())
    else:
        st.warning("No tasks fit the plan. Add tasks or increase the available minutes.")
