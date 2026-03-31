import datetime

import streamlit as st
from pawpal_system import DailyPlan, Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# Priority display helpers
_PRIORITY_COLOR = {"high": "🔴", "medium": "🟡", "low": "🟢"}
_PRIORITY_LABEL = {"high": "High", "medium": "Medium", "low": "Low"}


# ---------------------------------------------------------------------------
# Section 1 — Owner & Pet Setup
# ---------------------------------------------------------------------------
st.subheader("Owner & Pet Setup")

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
    st.success(f"Saved! Ready to plan {pet.name}'s day.")

# Persistent profile banner shown whenever a pet is loaded
if "pet" in st.session_state:
    p = st.session_state.pet
    o = st.session_state.owner
    st.info(
        f"**{p.name}** ({p.species}) · Owner: **{o.name}** · "
        f"Time budget: **{o.available_minutes} min**"
    )

# ---------------------------------------------------------------------------
# Section 2 — Add a Task
# ---------------------------------------------------------------------------
if "scheduler" in st.session_state:
    st.divider()
    st.subheader("Add a Task")

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
        st.success(f"Added **{task_title}** ({priority} priority, {duration} min).")

    # Live conflict hint — re-evaluated on every render, no button needed
    quick_warning = st.session_state.scheduler.quick_conflict_check()
    if quick_warning:
        st.warning(quick_warning)

    # ------------------------------------------------------------------
    # Task List — filter_tasks() + sort_by_time() + st.dataframe
    # ------------------------------------------------------------------
    st.divider()
    st.subheader("Task List")

    filter_status = st.radio(
        "Show", ["all", "pending", "completed"], horizontal=True
    )

    scheduler: Scheduler = st.session_state.scheduler
    completed_filter = {"all": None, "pending": False, "completed": True}[filter_status]

    filtered = scheduler.filter_tasks(
        pet_name=scheduler.pet.name,
        completed=completed_filter,
    )

    sorted_filtered = sorted(
        filtered,
        key=lambda t: (
            t.latest_start_time if t.latest_start_time else datetime.time(23, 59),
            -t.get_priority_value(),
        ),
    )

    if sorted_filtered:
        st.caption("Sorted by earliest deadline first, then priority — matching the scheduler's order.")

        rows = [
            {
                "Order": i + 1,
                "Task": t.title,
                "Priority": f"{_PRIORITY_COLOR[t.priority]} {_PRIORITY_LABEL[t.priority]}",
                "Duration (min)": t.duration_minutes,
                "Deadline": t.latest_start_time.strftime("%H:%M") if t.latest_start_time else "—",
                "Recurrence": t.recurrence.capitalize() if t.recurrence else "—",
                "Status": "Done ✓" if t.completed else "Pending",
            }
            for i, t in enumerate(sorted_filtered)
        ]

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Order":        st.column_config.NumberColumn(width="small"),
                "Task":         st.column_config.TextColumn(width="medium"),
                "Priority":     st.column_config.TextColumn(width="small"),
                "Duration (min)": st.column_config.NumberColumn(width="small"),
                "Deadline":     st.column_config.TextColumn(width="small"),
                "Recurrence":   st.column_config.TextColumn(width="small"),
                "Status":       st.column_config.TextColumn(width="small"),
            },
        )

        # Mark complete via scheduler.complete_task() so recurrence re-queues
        pending_titles = [t.title for t in scheduler.tasks if not t.completed]
        if pending_titles:
            col_sel, col_btn = st.columns([3, 1])
            with col_sel:
                task_to_complete = st.selectbox(
                    "Mark task complete",
                    ["(select a task)"] + pending_titles,
                    label_visibility="collapsed",
                )
            with col_btn:
                mark_clicked = st.button("Mark done", use_container_width=True)

            if mark_clicked and task_to_complete != "(select a task)":
                next_task = scheduler.complete_task(task_to_complete)
                if next_task is not None:
                    st.success(
                        f"**{task_to_complete}** complete. "
                        f"Next {next_task.recurrence} occurrence queued for **{next_task.due_date_str()}**."
                    )
                else:
                    st.success(f"**{task_to_complete}** marked complete.")
    else:
        st.info("No tasks match the current filter.")

# ---------------------------------------------------------------------------
# Section 3 — Conflict Detection
# ---------------------------------------------------------------------------
if "scheduler" in st.session_state and st.session_state.scheduler.tasks:
    st.divider()
    st.subheader("Conflict Detection")

    with st.expander("Run full conflict check", expanded=False):
        if st.button("Check now"):
            conflicts = st.session_state.scheduler.detect_conflicts()
            if conflicts:
                st.error(f"{len(conflicts)} conflict(s) found. Review and adjust deadlines or durations.")
                for c in conflicts:
                    st.warning(c)
            else:
                st.success("All clear — no deadline misses, shared deadlines, or time overlaps detected.")

# ---------------------------------------------------------------------------
# Section 4 — Today's Schedule
# ---------------------------------------------------------------------------
if "scheduler" in st.session_state:
    st.divider()
    st.subheader("Today's Schedule")

    if st.button("Generate schedule"):
        plan: DailyPlan = st.session_state.scheduler.generate_plan()
        summary = plan.get_summary()

        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Scheduled", summary["scheduled_count"])
        col_b.metric("Dropped", summary["dropped_count"])
        col_c.metric("Total time (min)", summary["total_duration_minutes"])
        col_d.metric("Conflicts", summary["conflict_count"])

        if plan.scheduled:
            st.markdown("#### Scheduled")
            for task, reason in plan.scheduled:
                start_str = task.scheduled_start.strftime("%H:%M") if task.scheduled_start else "?"
                with st.container(border=True):
                    left, right = st.columns([5, 1])
                    with left:
                        badges = ""
                        if task.is_urgent():
                            badges += " `deadline`"
                        if task.is_recurring():
                            badges += f" `{task.recurrence}`"
                        st.markdown(f"**{start_str} — {task.title}**{badges}")
                        st.caption(f"{task.duration_minutes} min · {reason}")
                    with right:
                        st.markdown(
                            f"<div style='text-align:right;font-size:1.4rem;'>"
                            f"{_PRIORITY_COLOR[task.priority]}</div>",
                            unsafe_allow_html=True,
                        )

        if plan.dropped:
            st.markdown("#### Not scheduled")
            for task, reason in plan.dropped:
                with st.container(border=True):
                    st.markdown(f"~~{task.title}~~  \n{reason}")

        if plan.conflicts:
            st.markdown("#### Conflicts detected")
            for c in plan.conflicts:
                st.warning(c)
