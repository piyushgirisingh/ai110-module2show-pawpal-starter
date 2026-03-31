import streamlit as st
from pawpal_system import DailyPlan, Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")


# ---------------------------------------------------------------------------
# Section 1 — Add a Pet
# ---------------------------------------------------------------------------
st.subheader("Add a Pet")

owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input(
    "Minutes available today", min_value=10, max_value=480, value=90
)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
day_start = st.text_input("Day starts at (HH:MM)", value="06:00")

if st.button("Save owner & pet"):
    pet = Pet(name=pet_name, species=species, age=0)
    owner = Owner(name=owner_name, available_minutes=int(available_minutes), pets=[pet])
    st.session_state.pet = pet
    st.session_state.owner = owner
    st.session_state.scheduler = Scheduler(pet=pet, owner=owner, day_start=day_start)
    st.success(f"Saved! {owner.name} is caring for {pet.name}. ({pet.get_profile()})")

# ---------------------------------------------------------------------------
# Section 2 — Schedule a Task
# ---------------------------------------------------------------------------
if "scheduler" in st.session_state:
    st.divider()
    st.subheader("Schedule a Task")

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5 = st.columns(2)
    with col4:
        latest_start = st.text_input("Latest start time (HH:MM, optional)", value="")
    with col5:
        recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly"])

    if st.button("Add task"):
        task = Task(
            title=task_title,
            task_type="general",
            duration_minutes=int(duration),
            priority=priority,
            pet_name=st.session_state.pet.name,
            latest_start_time=latest_start.strip() if latest_start.strip() else None,
            recurrence=recurrence if recurrence != "none" else None,
        )
        st.session_state.scheduler.add_task(task)
        st.success(f"Task added: {task_title}")

    # ------------------------------------------------------------------
    # Feature 2 — Filter task list by status
    # ------------------------------------------------------------------
    st.divider()
    st.subheader("Task List")

    filter_status = st.radio(
        "Filter by status", ["all", "pending", "completed"], horizontal=True
    )

    current_tasks = st.session_state.scheduler.tasks
    if filter_status == "pending":
        display_tasks = [t for t in current_tasks if not t.completed]
    elif filter_status == "completed":
        display_tasks = [t for t in current_tasks if t.completed]
    else:
        display_tasks = current_tasks

    if display_tasks:
        st.table([
            {
                "title": t.title,
                "duration (min)": t.duration_minutes,
                "priority": t.priority,
                "deadline": t.latest_start_time.strftime("%H:%M") if t.latest_start_time else "—",
                "recurrence": t.recurrence or "—",
                "done": "✓" if t.completed else "",
            }
            for t in display_tasks
        ])

        # Mark a task complete
        task_to_complete = st.selectbox(
            "Mark task complete",
            ["(select)"] + [t.title for t in current_tasks if not t.completed],
        )
        if st.button("Mark complete") and task_to_complete != "(select)":
            for t in current_tasks:
                if t.title == task_to_complete:
                    t.mark_complete()
                    st.success(f"Marked '{task_to_complete}' as complete.")
                    break
    else:
        st.info("No tasks match the current filter.")

# ---------------------------------------------------------------------------
# Section 3 — Conflict Detection
# ---------------------------------------------------------------------------
if "scheduler" in st.session_state and st.session_state.scheduler.tasks:
    st.divider()
    st.subheader("Conflict Detection")

    if st.button("Check for conflicts"):
        conflicts = st.session_state.scheduler.detect_conflicts()
        if conflicts:
            for c in conflicts:
                st.warning(c)
        else:
            st.success("No conflicts detected — all tasks fit within their deadlines.")

# ---------------------------------------------------------------------------
# Section 4 — Today's Schedule
# ---------------------------------------------------------------------------
if "scheduler" in st.session_state:
    st.divider()
    st.subheader("Today's Schedule")

    if st.button("Generate schedule"):
        plan: DailyPlan = st.session_state.scheduler.generate_plan()
        st.text(plan.display())
        summary = plan.get_summary()
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Scheduled", summary["scheduled_count"])
        col_b.metric("Dropped", summary["dropped_count"])
        col_c.metric("Total time (min)", summary["total_duration_minutes"])
        col_d.metric("Conflicts", summary["conflict_count"])
