from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    weight: float
    health_notes: str = ""

    def get_info(self) -> str:
        pass


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str          # "low", "medium", or "high"
    category: str          # "walk", "feed", "groom", "meds", "enrichment"
    is_recurring: bool = False

    def get_priority_score(self) -> int:
        pass

    def get_details(self) -> str:
        pass


@dataclass
class ScheduledTask:
    task: Task
    start_time: str        # e.g. "08:00"
    end_time: str          # e.g. "08:30"

    def get_time_block(self) -> str:
        pass


class Owner:
    def __init__(self, name: str, email: str, phone: int, preferences: Optional[dict] = None):
        self.name = name
        self.email = email
        self.phone = phone
        self.preferences: dict = preferences or {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, name: str) -> None:
        pass

    def get_pets(self) -> list[Pet]:
        pass

    def set_preferences(self, prefs: dict) -> None:
        pass


class DailyPlan:
    def __init__(self, date: str, owner: Owner, pet: Pet):
        self.date = date
        self.owner = owner
        self.pet = pet
        self.scheduled_tasks: list[ScheduledTask] = []

    def add_task(self, task: Task, start_time: str) -> None:
        pass

    def total_duration(self) -> int:
        pass

    def get_summary(self) -> str:
        pass

    def explain(self) -> str:
        pass


class Scheduler:
    def __init__(self, available_minutes: int, tasks: Optional[list[Task]] = None):
        self.available_minutes = available_minutes
        self.tasks: list[Task] = tasks or []

    def generate_plan(self, tasks: list[Task], available_minutes: int) -> DailyPlan:
        pass

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        pass

    def filter_by_time(self, tasks: list[Task], minutes: int) -> list[Task]:
        pass
