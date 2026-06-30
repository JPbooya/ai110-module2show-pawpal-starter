from datetime import datetime

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

if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name)

owner = st.session_state.owner

st.markdown("### Pets")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    owner.add_pet(Pet(pet_name, species))

if owner.get_pets():
    st.write("Current pets:")
    st.table([{"name": p.name, "species": p.species} for p in owner.get_pets()])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add a few tasks. These feed into the scheduler below.")

if owner.get_pets():
    pet_names = [p.name for p in owner.get_pets()]
    selected_pet_name = st.selectbox("Pet", pet_names)
    selected_pet = next(p for p in owner.get_pets() if p.name == selected_pet_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_description = st.text_input("Task description", value="Morning walk")
    with col2:
        task_time = st.text_input("Time", value="08:00")
    with col3:
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    col4, col5 = st.columns(2)
    with col4:
        duration_minutes = st.number_input("Duration (minutes)", min_value=5, value=30, step=5)
    with col5:
        day_of_week = None
        if frequency == "weekly":
            day_of_week = st.selectbox(
                "Day of week",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            )

    if st.button("Add task"):
        selected_pet.add_task(
            Task(task_description, task_time, frequency, duration_minutes=duration_minutes, day_of_week=day_of_week)
        )

    scheduler = Scheduler(owner)

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        col1, col2 = st.columns(2)
        with col1:
            filter_pet_name = st.selectbox("Filter by pet", ["All"] + pet_names)
        with col2:
            filter_status = st.selectbox("Filter by status", ["All", "pending", "completed"])

        filtered_tasks = scheduler.filter_tasks(
            pet_name=None if filter_pet_name == "All" else filter_pet_name,
            status=None if filter_status == "All" else filter_status
        )

        st.write("Current tasks:")
        st.table(
            [
                {
                    "description": t.description,
                    "time": t.time,
                    "frequency": t.frequency,
                    "day_of_week": t.day_of_week or "-",
                    "duration": t.duration_minutes,
                    "completed": t.completed,
                }
                for t in filtered_tasks
            ]
        )
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet first before adding tasks.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates today's schedule, sorted by time, across all pets.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    today_name = datetime.now().strftime("%A")
    schedule = scheduler.organize_by_time(day_of_week=today_name)

    if schedule:
        st.write(f"Today's Schedule ({today_name})")
        for task in schedule:
            st.write(f"{task.time} — {task.description} ({task.frequency})")

        conflict_warning = scheduler.check_for_conflicts(day_of_week=today_name)
        if conflict_warning:
            st.warning(conflict_warning)
    else:
        st.info("No tasks to schedule yet. Add a pet and a task above.")
