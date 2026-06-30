from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class Task:
    description: str
    time: str               # e.g. "08:00"
    frequency: str           # "once", "daily", "weekly"
    duration_minutes: int = 30
    day_of_week: str | None = None   # required for "weekly", e.g. "Monday"
    completed: bool = False
    last_completed_date: str | None = None   # ISO date, set by mark_complete

    def mark_complete(self, on: date | None = None) -> None:
        """Mark this task as completed, recording when."""
        self.completed = True
        self.last_completed_date = (on or date.today()).isoformat()

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.completed = False
        self.last_completed_date = None

    def next_occurrence(self) -> "Task | None":
        """Return a fresh pending Task for this task's next occurrence, or None for one-off tasks.

        Recurrence is handled by spawning a new instance (same description, time,
        frequency, duration, and day_of_week, but completed=False) rather than
        resetting this task in place, so the original remains a historical record
        of when that occurrence was completed.
        """
        if self.frequency not in ("daily", "weekly"):
            return None
        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            duration_minutes=self.duration_minutes,
            day_of_week=self.day_of_week,
        )

    def is_due_on(self, day_of_week: str) -> bool:
        """Whether this task occurs on the given weekday (e.g. "Monday").

        "once" and "daily" tasks are always due; "weekly" tasks are due only on
        their assigned day_of_week.
        """
        if self.frequency in ("once", "daily"):
            return True
        if self.frequency == "weekly":
            return self.day_of_week == day_of_week
        return False

    def start_minutes(self) -> int:
        """This task's start time as minutes since midnight (e.g. "08:30" -> 510)."""
        hours, minutes = map(int, self.time.split(":"))
        return hours * 60 + minutes

    def end_minutes(self) -> int:
        """This task's end time as minutes since midnight (start_minutes + duration_minutes)."""
        return self.start_minutes() + self.duration_minutes

    def overlaps(self, other: "Task") -> bool:
        """Whether this task's time window overlaps another's.

        Standard interval-overlap check: ranges [a_start, a_end) and
        [b_start, b_end) overlap if a_start < b_end and b_start < a_end.
        Relies on start_minutes/end_minutes, so it raises if either task has
        a malformed "HH:MM" time string.
        """
        return self.start_minutes() < other.end_minutes() and other.start_minutes() < self.end_minutes()


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

    def filter_tasks(self, pet_name: str | None = None, status: str | None = None) -> list[Task]:
        """Filter tasks by pet name and/or status ("pending" or "completed").

        Both filters apply together (AND) when both are given. Passing neither
        argument returns every task across all pets.
        """
        if pet_name is not None:
            pet = next((p for p in self.owner.get_pets() if p.name == pet_name), None)
            tasks = pet.get_tasks() if pet else []
        else:
            tasks = self.get_all_tasks()

        if status == "pending":
            tasks = [task for task in tasks if not task.completed]
        elif status == "completed":
            tasks = [task for task in tasks if task.completed]
        return tasks

    def get_due_tasks(self, day_of_week: str | None = None) -> list[Task]:
        """Return tasks that occur on the given weekday (defaults to today).

        Delegates the per-task due/not-due decision to Task.is_due_on, so
        "once"/"daily" tasks always pass and "weekly" tasks pass only on
        their assigned day.
        """
        day_of_week = day_of_week or datetime.now().strftime("%A")
        return [task for task in self.get_all_tasks() if task.is_due_on(day_of_week)]

    def find_owning_pet(self, task: Task) -> Pet | None:
        """Return the Pet that owns the given task, if any.

        Linear search across each pet's task list; used internally (e.g. by
        complete_task) so callers don't need to track ownership themselves.
        """
        return next((p for p in self.owner.get_pets() if task in p.get_tasks()), None)

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task complete; if it recurs, automatically schedule its next occurrence.

        Looks up the task's owning pet via find_owning_pet and appends the new
        occurrence (from Task.next_occurrence) to that pet's task list. The
        original task is left in place as a completed historical record.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            owning_pet = self.find_owning_pet(task)
            if owning_pet is not None:
                owning_pet.add_task(next_task)
        return next_task

    def organize_by_time(self, day_of_week: str | None = None) -> list[Task]:
        """Return tasks sorted chronologically by time, optionally limited to a weekday's due tasks.

        Sorts by the raw "HH:MM" time string rather than parsing it, since a
        zero-padded 24-hour string sorts identically to its numeric value.
        """
        tasks = self.get_due_tasks(day_of_week) if day_of_week else self.get_all_tasks()
        return sorted(tasks, key=lambda task: task.time)

    def find_conflicts(self, day_of_week: str | None = None) -> list[tuple[Task, Task]]:
        """Return pairs of same-day tasks whose time windows overlap, whether for the same pet or different pets.

        O(n^2) pairwise comparison using Task.overlaps. Because overlaps()
        parses each task's time into minutes, this raises if any due task has
        a malformed time string -- see check_for_conflicts for a version that
        can't crash.
        """
        due = self.get_due_tasks(day_of_week)
        conflicts = []
        for i, task_a in enumerate(due):
            for task_b in due[i + 1:]:
                if task_a.overlaps(task_b):
                    conflicts.append((task_a, task_b))
        return conflicts

    def check_for_conflicts(self, day_of_week: str | None = None) -> str:
        """Lightweight conflict check: groups same-day tasks by exact start time.

        Unlike find_conflicts (which parses times to compare duration-aware overlap
        windows and can raise on malformed time strings), this only compares the raw
        `time` string, so it never raises. Returns a warning message, or "" if no
        tasks share a start time.
        """
        due = self.get_due_tasks(day_of_week)
        by_time: dict[str, list[Task]] = {}
        for task in due:
            by_time.setdefault(task.time, []).append(task)

        warnings = []
        for time, tasks in by_time.items():
            if len(tasks) < 2:
                continue
            labels = []
            for task in tasks:
                pet = self.find_owning_pet(task)
                labels.append(f"{pet.name}'s {task.description}" if pet else task.description)
            warnings.append(f"{time}: " + " & ".join(labels))

        if not warnings:
            return ""
        return "Scheduling conflicts detected:\n" + "\n".join(warnings)
