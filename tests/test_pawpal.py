from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def make_task(title="Morning walk", priority="medium", duration=20,
              deadline=None, recurrence=None, pet_name=None):
    return Task(
        title=title,
        task_type="walk",
        duration_minutes=duration,
        priority=priority,
        latest_start_time=deadline,
        recurrence=recurrence,
        pet_name=pet_name,
    )


def make_scheduler(tasks, available_minutes=240, day_start="06:00"):
    pet = Pet(name="Mochi", species="dog", age=3)
    owner = Owner(name="Alex", available_minutes=available_minutes, pets=[pet])
    scheduler = Scheduler(pet=pet, owner=owner, day_start=day_start)
    scheduler.tasks = list(tasks)
    return scheduler


# ---------------------------------------------------------------------------
# Existing tests
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_to_pet_increases_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert pet.task_count() == 0
    pet.add_task(make_task("Morning walk"))
    assert pet.task_count() == 1
    pet.add_task(make_task("Feeding"))
    assert pet.task_count() == 2


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_earliest_deadline_first():
    """Tasks with earlier deadlines come before tasks with later deadlines."""
    late = make_task("Evening walk", deadline="17:00")
    early = make_task("Medication", deadline="07:30")
    no_dl = make_task("Playtime")  # no deadline — should be last

    scheduler = make_scheduler([late, early, no_dl])
    sorted_tasks = scheduler.sort_by_time()

    assert [t.title for t in sorted_tasks] == ["Medication", "Evening walk", "Playtime"]


def test_sort_same_deadline_high_priority_first():
    """Within the same deadline, higher priority tasks sort before lower priority ones."""
    low = make_task("Bath", priority="low", deadline="09:00")
    high = make_task("Medication", priority="high", deadline="09:00")
    med = make_task("Feeding", priority="medium", deadline="09:00")

    scheduler = make_scheduler([low, high, med])
    sorted_tasks = scheduler.sort_by_time()

    assert [t.title for t in sorted_tasks] == ["Medication", "Feeding", "Bath"]


def test_sort_no_deadline_tasks_ordered_by_priority():
    """Tasks with no deadline are all placed after deadline tasks, sorted by priority."""
    deadline_task = make_task("Morning meds", deadline="08:00")
    low = make_task("Toy time", priority="low")
    high = make_task("Grooming", priority="high")

    scheduler = make_scheduler([low, deadline_task, high])
    sorted_tasks = scheduler.sort_by_time()

    titles = [t.title for t in sorted_tasks]
    assert titles[0] == "Morning meds"       # deadline task always first
    assert titles.index("Grooming") < titles.index("Toy time")  # high before low


def test_sort_pet_with_no_tasks_returns_empty():
    """Sorting an empty task list returns an empty list without error."""
    scheduler = make_scheduler([])
    assert scheduler.sort_by_time() == []


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_complete_daily_task_creates_next_occurrence():
    """Completing a daily task appends a new task due tomorrow."""
    task = make_task("Morning walk", recurrence="daily", pet_name="Mochi")
    scheduler = make_scheduler([task])

    next_task = scheduler.complete_task("Morning walk")

    assert next_task is not None
    assert next_task.completed is False
    assert next_task.scheduled_start is None
    assert next_task.recurrence == "daily"
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert len(scheduler.tasks) == 2  # original + new occurrence


def test_complete_weekly_task_creates_occurrence_seven_days_out():
    """Completing a weekly task appends a new task due in 7 days."""
    task = make_task("Grooming brush", recurrence="weekly", pet_name="Mochi")
    scheduler = make_scheduler([task])

    next_task = scheduler.complete_task("Grooming brush")

    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(weeks=1)


def test_complete_nonrecurring_task_returns_none():
    """Completing a one-off task returns None and does not append a new task."""
    task = make_task("Vet visit")
    scheduler = make_scheduler([task])

    result = scheduler.complete_task("Vet visit")

    assert result is None
    assert len(scheduler.tasks) == 1  # no new task added


def test_complete_recurring_task_preserves_deadline():
    """The spawned next occurrence retains the original task's deadline time."""
    task = make_task("Thyroid meds", deadline="07:30", recurrence="daily", pet_name="Mochi")
    scheduler = make_scheduler([task])

    next_task = scheduler.complete_task("Thyroid meds")

    assert next_task is not None
    assert next_task.latest_start_time is not None
    assert next_task.latest_start_time.strftime("%H:%M") == "07:30"


def test_complete_nonexistent_task_returns_none():
    """complete_task() with an unknown title returns None without crashing."""
    scheduler = make_scheduler([make_task("Bath")])
    result = scheduler.complete_task("Ghost task")
    assert result is None


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_two_tasks_same_deadline_flagged_as_conflict():
    """Two tasks with identical deadlines trigger a shared-deadline conflict."""
    t1 = make_task("Feeding", deadline="08:00", pet_name="Mochi")
    t2 = make_task("Medication", deadline="08:00", pet_name="Mochi")
    scheduler = make_scheduler([t1, t2])

    conflicts = scheduler.detect_conflicts()

    assert any("08:00" in c for c in conflicts), (
        f"Expected a shared-deadline conflict at 08:00, got: {conflicts}"
    )


def test_overlapping_tasks_detected():
    """A 60-min task at 06:00 and a 30-min task at 06:30 overlap and must be flagged."""
    long_task = make_task("Long walk", duration=60, deadline="06:00", pet_name="Mochi")
    overlap = make_task("Feeding", duration=30, deadline="06:30", pet_name="Mochi")
    scheduler = make_scheduler([long_task, overlap])

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) > 0, f"Expected at least one conflict, got none. Tasks: {scheduler.tasks}"


def test_non_overlapping_tasks_produce_no_conflicts():
    """Sequential tasks that don't overlap should produce zero conflicts."""
    t1 = make_task("Morning walk", duration=30, deadline="07:00", pet_name="Mochi")
    t2 = make_task("Feeding", duration=20, deadline="08:00", pet_name="Mochi")
    scheduler = make_scheduler([t1, t2])

    conflicts = scheduler.detect_conflicts()

    assert conflicts == [], f"Expected no conflicts, got: {conflicts}"


def test_quick_conflict_check_returns_none_for_clean_schedule():
    """quick_conflict_check() returns None when tasks don't overlap."""
    t1 = make_task("Walk", duration=30, deadline="07:00", pet_name="Mochi")
    t2 = make_task("Feed", duration=20, deadline="08:00", pet_name="Mochi")
    scheduler = make_scheduler([t1, t2])

    assert scheduler.quick_conflict_check() is None


def test_quick_conflict_check_returns_warning_for_overlap():
    """quick_conflict_check() returns a warning string when tasks overlap."""
    long_task = make_task("Long walk", duration=60, deadline="06:00", pet_name="Mochi")
    overlap = make_task("Feeding", duration=30, deadline="06:30", pet_name="Mochi")
    scheduler = make_scheduler([long_task, overlap])

    result = scheduler.quick_conflict_check()

    assert result is not None and result.startswith("Warning:")
