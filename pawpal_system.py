from dataclasses import dataclass, field


@dataclass
class Task:
    description: str
    time: str               # e.g. "08:00"
    frequency: str           # "once", "daily", "weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.completed = False


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return this pet's list of tasks."""
        return self.tasks


class Owner:
    def __init__(self, name: str):
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return this owner's list of pets."""
        return self.pets

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks across all of this owner's pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks across all of the owner's pets."""
        return self.owner.get_all_tasks()

    def get_pending_tasks(self) -> list[Task]:
        """Return all tasks that are not yet completed."""
        return [task for task in self.get_all_tasks() if not task.completed]

    def get_completed_tasks(self) -> list[Task]:
        """Return all tasks that have been completed."""
        return [task for task in self.get_all_tasks() if task.completed]

    def get_tasks_by_frequency(self, frequency: str) -> list[Task]:
        """Return all tasks matching the given frequency."""
        return [task for task in self.get_all_tasks() if task.frequency == frequency]

    def get_tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Return all tasks belonging to a specific pet."""
        return pet.get_tasks()

    def organize_by_time(self) -> list[Task]:
        """Return all tasks sorted chronologically by time."""
        return sorted(self.get_all_tasks(), key=lambda task: task.time)
