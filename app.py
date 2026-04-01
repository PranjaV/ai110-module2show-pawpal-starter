import streamlit as st
from datetime import datetime
from pathlib import Path

from pawpal_system import Owner, Pet, Scheduler, Task

DATA_FILE = Path("pawpal_data.json")

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
PawPal+ helps you manage pet care tasks with smarter scheduling.

Features in this app:
- Multi-pet tracking
- Sorted daily schedule
- Conflict detection warnings
- Filtering by pet and completion status
- Recurring task support (daily and weekly)
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


if "owner" not in st.session_state:
    st.session_state.owner = Owner.load_from_json(str(DATA_FILE))

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)


owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

st.divider()

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

col_persist_1, col_persist_2, col_persist_3 = st.columns(3)
with col_persist_1:
    if st.button("💾 Save Data"):
        owner.save_to_json(str(DATA_FILE))
        st.success("Saved to pawpal_data.json")
with col_persist_2:
    if st.button("🔄 Reload Data"):
        st.session_state.owner = Owner.load_from_json(str(DATA_FILE))
        st.session_state.scheduler = Scheduler(st.session_state.owner)
        st.rerun()
with col_persist_3:
    if st.button("🗑️ Reset Data"):
        if DATA_FILE.exists():
            DATA_FILE.unlink()
        st.session_state.owner = Owner(name="Jordan")
        st.session_state.scheduler = Scheduler(st.session_state.owner)
        st.rerun()

st.subheader("Add Pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", placeholder="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet_clicked = st.form_submit_button("Add pet")

if add_pet_clicked:
    if not pet_name.strip():
        st.warning("Please enter a pet name.")
    elif owner.get_pet(pet_name.strip()):
        st.warning(f"A pet named '{pet_name.strip()}' already exists.")
    else:
        owner.add_pet(Pet(name=pet_name.strip(), species=species))
        st.success(f"Added pet: {pet_name.strip()} ({species})")

st.markdown("### Tasks")
st.caption("Add tasks and let the scheduler organize your day.")

if not owner.pets:
    st.info("Add a pet first to start creating tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        pet_options = [pet.name for pet in owner.pets]
        selected_pet_name = st.selectbox("Pet", pet_options)
        task_title = st.text_input("Task title", placeholder="Morning walk")

        col1, col2, col3 = st.columns(3)
        with col1:
            task_time = st.text_input("Time (HH:MM)", value="08:00")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)

        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=0)
        add_task_clicked = st.form_submit_button("Add task")

    if add_task_clicked:
        pet = owner.get_pet(selected_pet_name)
        if pet is None:
            st.error("Selected pet not found.")
        elif not task_title.strip():
            st.warning("Please provide a task title.")
        else:
            try:
                # Validate the time format early to avoid invalid schedules.
                datetime.strptime(task_time, "%H:%M")
                pet.add_task(
                    Task(
                        description=task_title.strip(),
                        time=task_time,
                        priority=priority,
                        frequency=frequency,
                        duration_minutes=int(duration),
                    )
                )
                st.success(f"Added task '{task_title.strip()}' for {pet.name}.")
            except ValueError:
                st.error("Time must be in HH:MM format, for example 07:30.")

st.divider()

st.subheader("Schedule")

all_records = scheduler.get_schedule(include_completed=True)
show_completed = st.checkbox("Show completed tasks", value=False)

filter_options = ["All"] + [pet.name for pet in owner.pets]
pet_filter = st.selectbox("Filter by pet", filter_options)

filtered_records = scheduler.filter_tasks(
    records=all_records,
    pet_name=None if pet_filter == "All" else pet_filter,
    completed=None if show_completed else False,
)
sorted_records = scheduler.sort_by_time(filtered_records)

if sorted_records:
    rows = []
    for pet, task in sorted_records:
        priority_badge = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}.get(
            task.priority.lower(), task.priority
        )
        status_badge = "✅ Done" if task.completed else "⏳ Pending"
        freq_badge = {"daily": "🔁 Daily", "weekly": "📆 Weekly", "once": "• Once"}.get(
            task.frequency.lower(), task.frequency
        )
        rows.append(
            {
                "🐾 Pet": pet.name,
                "📝 Task": task.description,
                "Date": task.due_date.isoformat(),
                "Time": task.time,
                "Priority": priority_badge,
                "Frequency": freq_badge,
                "Duration (min)": task.duration_minutes,
                "Status": status_badge,
            }
        )
    st.dataframe(rows, use_container_width=True)
else:
    st.info("No tasks match the current filters.")

conflicts = scheduler.detect_conflicts(
    records=[record for record in sorted_records if not record[1].completed]
)
for warning in conflicts:
    st.warning(warning)

overlap_conflicts = scheduler.detect_time_overlap_conflicts(
    records=[record for record in sorted_records if not record[1].completed]
)
for warning in overlap_conflicts:
    st.warning(warning)

st.subheader("Priority Time-Blocked Plan")
planned_rows, plan_warnings = scheduler.generate_time_blocked_plan(
    records=[record for record in sorted_records if not record[1].completed]
)
if planned_rows:
    st.dataframe(planned_rows, use_container_width=True)
for warning in plan_warnings:
    st.info(warning)

st.subheader("Next Available Slot Finder")
slot_col_1, slot_col_2, slot_col_3 = st.columns(3)
with slot_col_1:
    target_date = st.date_input("Target date")
with slot_col_2:
    requested_minutes = st.number_input("Duration", min_value=15, max_value=240, value=30, step=15)
with slot_col_3:
    start_after = st.text_input("Start after (HH:MM)", value="06:00")

if st.button("Find Next Slot"):
    try:
        datetime.strptime(start_after, "%H:%M")
        slot = scheduler.next_available_slot(
            target_date=target_date,
            duration_minutes=int(requested_minutes),
            start_time=start_after,
        )
        if slot:
            st.success(f"Next available slot: {slot}")
        else:
            st.error("No slot available in the configured day window.")
    except ValueError:
        st.error("Start time must be HH:MM format.")

st.subheader("Mark Task Complete")
if not owner.pets:
    st.info("Add pets and tasks first.")
else:
    available_options = []
    option_to_target = {}
    for pet in owner.pets:
        for index, task in enumerate(pet.tasks):
            if task.completed:
                continue
            label = f"{pet.name} | {task.description} | {task.due_date} {task.time}"
            available_options.append(label)
            option_to_target[label] = (pet.name, index)

    if not available_options:
        st.success("All current tasks are completed.")
    else:
        selected_label = st.selectbox("Choose task", available_options)
        if st.button("Mark selected task complete"):
            pet_name_value, task_index_value = option_to_target[selected_label]
            scheduler.mark_task_complete(pet_name_value, task_index_value)
            st.success(
                "Task completed. If recurring, the next instance has been scheduled automatically."
            )
