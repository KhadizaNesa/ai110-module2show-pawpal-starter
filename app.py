import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

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
owner_name = st.text_input("Owner name", value="Jordan")

# Create the Owner once and keep it in session_state so it survives reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
owner = st.session_state.owner
owner.name = owner_name  # keep the stored owner's name in sync with the input

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
        priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    task_time = st.text_input("Time", value="08:00")
    frequency = st.selectbox("Frequency", ["daily", "weekly"])

    # Task stores priority as a number (higher = more important),
    # so translate the words into numbers.
    priority_numbers = {"low": 1, "medium": 3, "high": 5}

    if st.button("Add task"):
        # Find the Pet object the user picked...
        chosen_pet = next(p for p in owner.get_pets() if p.name == chosen_pet_name)
        # ...then Pet.add_task() attaches the new Task to it.
        chosen_pet.add_task(
            Task(
                description=task_title,
                time=task_time,
                frequency=frequency,
                priority=priority_numbers[priority_label],
                duration_minutes=int(duration),
            )
        )
        st.success(f"Added '{task_title}' to {chosen_pet_name}.")

    # Show every task across all of the owner's pets.
    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("Current tasks:")
        for task in all_tasks:
            st.write("- " + task.get_info())
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
    scheduler = Scheduler()
    plan = scheduler.generate_daily_plan(owner, available_minutes=int(available_minutes))
    if plan:
        st.write(f"Daily plan for {owner.name} ({int(available_minutes)} minutes):")
        for task in plan:
            st.write("- " + task.get_info())
    else:
        st.warning("No tasks fit the plan. Add tasks or increase the available minutes.")
