from datetime import date, time as Time, timedelta


class Pet:
    def __init__(self, name: str, species: str, age: int, special_needs: list[str] = None):
        self.name = name
        self.species = species
        self.age = age
        self.special_needs = special_needs if special_needs is not None else []
        self.tasks: list["Task"] = []

    def add_task(self, task: "Task") -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def task_count(self) -> int:
        """Return the number of tasks assigned to this pet."""
        return len(self.tasks)

    def get_profile(self) -> str:
        """Return a formatted summary of the pet's name, species, age, and special needs."""
        needs = ", ".join(self.special_needs) if self.special_needs else "none"
        return f"{self.name} ({self.species}, age {self.age}) — special needs: {needs}"


class Owner:
    def __init__(self, name: str, available_minutes: int, pets: list["Pet"] = None):
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = pets if pets is not None else []

    def get_time_budget(self) -> int:
        """Return the owner's total available minutes for the day."""
        return self.available_minutes


class Task:
    VALID_PRIORITIES = {"low", "medium", "high"}
    VALID_RECURRENCES = {None, "daily", "weekly"}
    _PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}

    def __init__(
        self,
        title: str,
        task_type: str,
        duration_minutes: int,
        priority: str,
        pet_name: str = None,
        latest_start_time: str = None,
        recurrence: str = None,
        due_date: date | None = None,
    ):
        if priority not in self.VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {self.VALID_PRIORITIES}, got '{priority}'")
        if recurrence not in self.VALID_RECURRENCES:
            raise ValueError(f"recurrence must be one of {self.VALID_RECURRENCES}, got '{recurrence}'")

        self.title = title
        self.task_type = task_type
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.pet_name = pet_name
        self.latest_start_time: Time | None = (
            Time.fromisoformat(latest_start_time) if latest_start_time else None
        )
        self.recurrence: str | None = recurrence
        self.due_date: date | None = due_date
        self.completed: bool = False
        # Assigned by generate_plan; None until scheduled
        self.scheduled_start: Time | None = None

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def get_priority_value(self) -> int:
        """Return a numeric priority (low=1, medium=2, high=3) for sorting."""
        return self._PRIORITY_MAP[self.priority]

    def is_urgent(self) -> bool:
        """Return True if the task has a latest_start_time constraint."""
        return self.latest_start_time is not None

    def is_recurring(self) -> bool:
        """Return True if the task repeats on a schedule."""
        return self.recurrence is not None

    def due_date_str(self) -> str:
        """Return the due date as an ISO string, or 'no date' if unset."""
        return self.due_date.isoformat() if self.due_date is not None else "no date"


class DailyPlan:
    def __init__(self, pet: "Pet", owner: "Owner"):
        self.pet = pet
        self.owner = owner
        self.scheduled: list[tuple[Task, str]] = []
        self.dropped: list[tuple[Task, str]] = []
        self.conflicts: list[str] = []

    @property
    def total_duration(self) -> int:
        """Return the total duration in minutes of all scheduled tasks."""
        return sum(task.duration_minutes for task, _ in self.scheduled)

    def display(self) -> str:
        """Return the full daily plan as a human-readable string."""
        lines = [f"Daily plan for {self.pet.name} (owner: {self.owner.name})", ""]
        for i, (task, reason) in enumerate(self.scheduled, start=1):
            start_str = task.scheduled_start.strftime("%H:%M") if task.scheduled_start else "?"
            recur_tag = f" [{task.recurrence}]" if task.is_recurring() else ""
            lines.append(
                f"{i}. [{start_str}] {task.title}{recur_tag} ({task.duration_minutes} min) — {reason}"
            )
        if self.dropped:
            lines.append("\nNot scheduled:")
            for task, reason in self.dropped:
                lines.append(f"  - {task.title}: {reason}")
        if self.conflicts:
            lines.append("\nConflicts detected:")
            for c in self.conflicts:
                lines.append(f"  ! {c}")
        lines.append(f"\nTotal time: {self.total_duration} min")
        return "\n".join(lines)

    def get_summary(self) -> dict:
        """Return scheduled/dropped counts, total duration, and conflict count as a dict."""
        return {
            "scheduled_count": len(self.scheduled),
            "dropped_count": len(self.dropped),
            "total_duration_minutes": self.total_duration,
            "conflict_count": len(self.conflicts),
        }


class Scheduler:
    def __init__(self, pet: Pet, owner: Owner, day_start: str = "06:00"):
        self.pet = pet
        self.owner = owner
        self.tasks: list[Task] = []
        self._day_start = Time.fromisoformat(day_start)

    def add_task(self, task: Task) -> None:
        """Add a task to the scheduler's pending task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove the first matching task from the pending list by title."""
        for i, t in enumerate(self.tasks):
            if t.title == title:
                del self.tasks[i]
                return

    # ------------------------------------------------------------------
    # Feature 1 — Sort by time (earliest deadline first, then priority)
    # ------------------------------------------------------------------
    def _sort_tasks(self) -> list[Task]:
        """Return tasks sorted by earliest deadline first, then by descending priority.

        Tasks with no deadline sort after all deadline-constrained tasks.
        Within the same deadline bucket, higher priority comes first.
        """
        def sort_key(t: Task):
            deadline = t.latest_start_time if t.latest_start_time else Time(23, 59)
            return (deadline, -t.get_priority_value())

        return sorted(self.tasks, key=sort_key)

    def sort_by_time(self) -> list[Task]:
        """Return the task list sorted by earliest latest_start_time first.

        Tasks without a deadline are placed after all deadline-constrained tasks.
        Within the same deadline, higher-priority tasks come first.
        """
        return self._sort_tasks()

    def _fits_in_budget(self, task: Task, minutes_used: int) -> bool:
        """Return True if the task fits within the owner's remaining time budget."""
        return minutes_used + task.duration_minutes <= self.owner.get_time_budget()

    def complete_task(self, title: str) -> "Task | None":
        """Mark the first matching task complete and enqueue the next occurrence.

        If the task has recurrence='daily' or 'weekly', a fresh copy is appended
        to self.tasks with completed=False and scheduled_start cleared, representing
        the next occurrence.  Returns the new Task if one was created, else None.
        """
        target = next((t for t in self.tasks if t.title == title), None)
        if target is None:
            return None

        target.mark_complete()

        if not target.is_recurring():
            return None

        recurrence_delta = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}
        next_due = date.today() + recurrence_delta[target.recurrence]

        next_task = Task(
            title=target.title,
            task_type=target.task_type,
            duration_minutes=target.duration_minutes,
            priority=target.priority,
            pet_name=target.pet_name,
            latest_start_time=(
                target.latest_start_time.strftime("%H:%M")
                if target.latest_start_time else None
            ),
            recurrence=target.recurrence,
            due_date=next_due,
        )
        self.tasks.append(next_task)
        return next_task

    # ------------------------------------------------------------------
    # Feature 2 — Filter tasks by pet name and/or completion status
    # ------------------------------------------------------------------
    def filter_tasks(self, pet_name: str = None, completed: bool = None) -> list[Task]:
        """Return tasks matching the given pet_name and/or completed status.

        Pass None for either argument to skip that filter.
        """
        result = self.tasks
        if pet_name is not None:
            result = [t for t in result if t.pet_name == pet_name]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        return result

    # ------------------------------------------------------------------
    # Feature 4 — Conflict detection
    # ------------------------------------------------------------------
    def _build_intervals(self) -> list[tuple["Task", int, int]]:
        """Return (task, start_min, end_min) for every task.

        If a task has a latest_start_time, that is treated as its intended
        start time.  Tasks without one are placed sequentially from day_start,
        slotted in after all deadline-pinned tasks that precede them.
        """
        intervals: list[tuple[Task, int, int]] = []
        sequential_cursor = self._day_start.hour * 60 + self._day_start.minute

        for task in self._sort_tasks():
            if task.latest_start_time is not None:
                start = task.latest_start_time.hour * 60 + task.latest_start_time.minute
            else:
                start = sequential_cursor

            end = start + task.duration_minutes
            intervals.append((task, start, end))
            sequential_cursor = max(sequential_cursor, end)

        return intervals

    def _deadline_conflicts(self) -> list[str]:
        """Return deadline-miss and shared-deadline conflict messages."""
        conflicts = []
        cursor = self._day_start.hour * 60 + self._day_start.minute
        deadline_map: dict[Time, list[str]] = {}

        for task in self._sort_tasks():
            if task.latest_start_time is not None:
                deadline_min = task.latest_start_time.hour * 60 + task.latest_start_time.minute
                if cursor > deadline_min:
                    actual = f"{cursor // 60:02d}:{cursor % 60:02d}"
                    conflicts.append(
                        f"'{task.title}' must start by "
                        f"{task.latest_start_time.strftime('%H:%M')} "
                        f"but sequential cursor reaches it at {actual}"
                    )
                deadline_map.setdefault(task.latest_start_time, []).append(task.title)
            cursor += task.duration_minutes

        for deadline, titles in deadline_map.items():
            if len(titles) > 1:
                conflicts.append(
                    f"Multiple tasks share deadline {deadline.strftime('%H:%M')}: "
                    + ", ".join(f"'{t}'" for t in titles)
                )
        return conflicts

    def _overlap_conflicts(self, intervals: list[tuple["Task", int, int]]) -> list[str]:
        """Return overlap conflict messages for all overlapping task pairs."""
        conflicts = []
        for i, (task_a, start_a, end_a) in enumerate(intervals):
            for task_b, start_b, end_b in intervals[i + 1:]:
                if start_a < end_b and start_b < end_a:
                    fmt = lambda t, s, e: (  # noqa: E731
                        f"'{t.title}' ({t.pet_name or 'unknown'}, "
                        f"{s // 60:02d}:{s % 60:02d}–{e // 60:02d}:{e % 60:02d})"
                    )
                    conflicts.append(f"Overlap: {fmt(task_a, start_a, end_a)} conflicts with {fmt(task_b, start_b, end_b)}")
        return conflicts

    def quick_conflict_check(self) -> str | None:
        """Lightweight conflict check — returns a single warning string or None.

        Uses a set of occupied minute-slots instead of pairwise comparison.
        Runs in O(n * d) time (n tasks, d average duration) and never raises;
        any unexpected error is caught and returned as a warning itself.
        Returns None when no conflict is found.
        """
        try:
            occupied: dict[int, str] = {}  # minute -> task title that claimed it
            for task, start, end in self._build_intervals():
                for minute in range(start, end):
                    if minute in occupied:
                        owner_title = occupied[minute]
                        hh, mm = minute // 60, minute % 60
                        return (
                            f"Warning: '{task.title}' overlaps with '{owner_title}' "
                            f"at {hh:02d}:{mm:02d}"
                        )
                    occupied[minute] = task.title
            return None
        except Exception as exc:  # noqa: BLE001
            return f"Warning: conflict check could not complete — {exc}"

    def detect_conflicts(self) -> list[str]:
        """Return all conflict messages for the current task list.

        Three conflict types are detected:
          1. Deadline miss — sequential cursor overtakes a task's latest_start_time.
          2. Shared deadline — two or more tasks share the exact same deadline.
          3. Time overlap — two tasks have overlapping [start, end) windows,
             for the same pet or across different pets.
        """
        return self._deadline_conflicts() + self._overlap_conflicts(self._build_intervals())

    # ------------------------------------------------------------------
    # Feature 3 — Recurring tasks + generate_plan with start-time tracking
    # ------------------------------------------------------------------
    def generate_plan(self) -> DailyPlan:
        """Sort and schedule tasks within the time budget, returning a DailyPlan.

        Each scheduled task receives a scheduled_start time based on a running
        clock starting at day_start.  Recurring tasks are noted in their reason
        string.  Conflicts are detected and attached to the plan.
        """
        plan = DailyPlan(pet=self.pet, owner=self.owner)
        minutes_used = 0
        current_minutes = self._day_start.hour * 60 + self._day_start.minute

        for task in self._sort_tasks():
            if self._fits_in_budget(task, minutes_used):
                # Assign start time
                task.scheduled_start = Time(current_minutes // 60, current_minutes % 60)

                reason = f"priority={task.priority}"
                if task.is_urgent():
                    reason += f", must start by {task.latest_start_time.strftime('%H:%M')}"
                if task.is_recurring():
                    reason += f", recurs {task.recurrence}"

                plan.scheduled.append((task, reason))
                minutes_used += task.duration_minutes
                current_minutes += task.duration_minutes
            else:
                plan.dropped.append((task, "insufficient time remaining in day"))

        plan.conflicts = self.detect_conflicts()
        return plan
