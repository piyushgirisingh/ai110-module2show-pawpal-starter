class Pet:
    def __init__(self, name: str, species: str, age: int, special_needs: list[str] = None):
        self.name = name
        self.species = species
        self.age = age
        self.special_needs = special_needs if special_needs is not None else []

    def get_profile(self) -> str:
        pass


class Owner:
    def __init__(self, name: str, available_minutes: int):
        self.name = name
        self.available_minutes = available_minutes

    def get_time_budget(self) -> int:
        pass


class Task:
    def __init__(
        self,
        title: str,
        task_type: str,
        duration_minutes: int,
        priority: str,
        latest_start_time: str = None,
    ):
        self.title = title
        self.task_type = task_type
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.latest_start_time = latest_start_time

    def get_priority_value(self) -> int:
        pass

    def is_urgent(self) -> bool:
        pass


class DailyPlan:
    def __init__(self):
        self.scheduled: list[tuple[Task, str]] = []
        self.dropped: list[tuple[Task, str]] = []
        self.total_duration: int = 0

    def display(self) -> str:
        pass

    def get_summary(self) -> dict:
        pass


class Scheduler:
    def __init__(self, pet: Pet, owner: Owner):
        self.pet = pet
        self.owner = owner
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, title: str) -> None:
        pass

    def generate_plan(self) -> DailyPlan:
        pass
