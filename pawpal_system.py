from datetime import time as Time


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

    def __init__(
        self,
        title: str,
        task_type: str,
        duration_minutes: int,
        priority: str,
        pet_name: str = None,
        latest_start_time: str = None,
    ):
        if priority not in self.VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {self.VALID_PRIORITIES}, got '{priority}'")

        self.title = title
        self.task_type = task_type
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.pet_name = pet_name
        self.latest_start_time: Time | None = (
            Time.fromisoformat(latest_start_time) if latest_start_time else None
        )
        self.completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def get_priority_value(self) -> int:
        """Return a numeric priority (low=1, medium=2, high=3) for sorting."""
        return {"low": 1, "medium": 2, "high": 3}[self.priority]

    def is_urgent(self) -> bool:
        """Return True if the task has a latest_start_time constraint."""
        return self.latest_start_time is not None


class DailyPlan:
    def __init__(self, pet: "Pet", owner: "Owner"):
        self.pet = pet
        self.owner = owner
        self.scheduled: list[tuple[Task, str]] = []
        self.dropped: list[tuple[Task, str]] = []

    @property
    def total_duration(self) -> int:
        """Return the total duration in minutes of all scheduled tasks."""
        return sum(task.duration_minutes for task, _ in self.scheduled)

    def display(self) -> str:
        """Return the full daily plan as a human-readable string."""
        lines = [f"Daily plan for {self.pet.name} (owner: {self.owner.name})", ""]
        for i, (task, reason) in enumerate(self.scheduled, start=1):
            lines.append(f"{i}. {task.title} ({task.duration_minutes} min) — {reason}")
        if self.dropped:
            lines.append("\nNot scheduled:")
            for task, reason in self.dropped:
                lines.append(f"  - {task.title}: {reason}")
        lines.append(f"\nTotal time: {self.total_duration} min")
        return "\n".join(lines)

    def get_summary(self) -> dict:
        """Return scheduled/dropped counts and total duration as a dict."""
        return {
            "scheduled_count": len(self.scheduled),
            "dropped_count": len(self.dropped),
            "total_duration_minutes": self.total_duration,
        }


class Scheduler:
    def __init__(self, pet: Pet, owner: Owner):
        self.pet = pet
        self.owner = owner
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to the scheduler's pending task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove a task from the pending list by its title."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def _sort_tasks(self) -> list[Task]:
        """Return tasks sorted by priority then urgency, highest first."""
        return sorted(self.tasks, key=lambda t: (t.get_priority_value(), t.is_urgent()), reverse=True)

    def _fits_in_budget(self, task: Task, minutes_used: int) -> bool:
        """Return True if the task fits within the owner's remaining time budget."""
        return minutes_used + task.duration_minutes <= self.owner.get_time_budget()

    def generate_plan(self) -> DailyPlan:
        """Sort and schedule tasks within the time budget, returning a DailyPlan."""
        plan = DailyPlan(pet=self.pet, owner=self.owner)
        minutes_used = 0
        for task in self._sort_tasks():
            if self._fits_in_budget(task, minutes_used):
                reason = f"priority={task.priority}"
                if task.is_urgent():
                    reason += f", must start by {task.latest_start_time.strftime('%H:%M')}"
                plan.scheduled.append((task, reason))
                minutes_used += task.duration_minutes
            else:
                plan.dropped.append((task, "insufficient time remaining in day"))
        return plan
