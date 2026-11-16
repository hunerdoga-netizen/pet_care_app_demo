"""PawPal+ logic layer: Owner, Commitment, Pet, Task and Scheduler."""

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from typing import List, Optional

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Commitment:
    """A block of time the owner is busy, e.g. work from 09:00 to 17:00."""

    label: str
    start: str  # "HH:MM"
    end: str  # "HH:MM"

    def overlaps(self, time: str) -> bool:
        """Return True if the given "HH:MM" time falls inside this commitment."""
        return self.start <= time < self.end


@dataclass
class Task:
    """One care activity (medicine, feeding, walk, appointment)."""

    description: str
    type: str  # "medicine", "feeding", "walk", "appointment", ...
    time: str  # "HH:MM"
    priority: str = "medium"  # "low", "medium" or "high"
    frequency: str = "once"  # "once", "daily" or "weekly"
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def mark_complete(self) -> Optional["Task"]:
        """Tick this task as done; return the next occurrence if it recurs."""
        self.completed = True
        if self.frequency == "daily":
            step = timedelta(days=1)
        elif self.frequency == "weekly":
            step = timedelta(weeks=1)
        else:
            return None
        return replace(self, due_date=self.due_date + step, completed=False)


@dataclass
class Pet:
    """One animal and the tasks that belong to it."""

    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        self.tasks.append(task)


@dataclass
class Owner:
    """The user: owns pets and has busy times (commitments)."""

    name: str
    pets: List[Pet] = field(default_factory=list)
    commitments: List[Commitment] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def add_commitment(self, commitment: Commitment) -> None:
        """Add a busy block to this owner's schedule."""
        self.commitments.append(commitment)

    def get_all_tasks(self) -> List[Task]:
        """Return every task from every pet together."""
        return [task for pet in self.pets for task in pet.tasks]

    def pet_for(self, task: Task) -> Optional[Pet]:
        """Return the pet that owns the given task."""
        for pet in self.pets:
            if any(t is task for t in pet.tasks):
                return pet
        return None


class Scheduler:
    """The brain: builds the daily plan from all of an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def get_tasks_for(self, day: date) -> List[Task]:
        """Return all tasks (across all pets) due on the given day."""
        return [t for t in self.owner.get_all_tasks() if t.due_date == day]

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks in chronological order using their "HH:MM" time."""
        return sorted(tasks, key=lambda t: t.time)

    def build_daily_plan(self, day: date) -> List[Task]:
        """Return the day's tasks ordered by priority (high first), then time."""
        return sorted(
            self.get_tasks_for(day),
            key=lambda t: (PRIORITY_ORDER.get(t.priority, 1), t.time),
        )

    def filter_tasks(
        self, pet_name: Optional[str] = None, completed: Optional[bool] = None
    ) -> List[Task]:
        """Return tasks filtered by pet name and/or completion status."""
        tasks = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is None or task.completed == completed:
                    tasks.append(task)
        return tasks

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task and add its next occurrence to the same pet."""
        pet = self.owner.pet_for(task)
        next_task = task.mark_complete()
        if next_task and pet:
            pet.add_task(next_task)
        return next_task

    def detect_conflicts(self, day: date) -> List[str]:
        """Return warning messages for tasks sharing the same time on a day."""
        by_time = {}
        for task in self.get_tasks_for(day):
            by_time.setdefault(task.time, []).append(task)
        warnings = []
        for time, tasks in sorted(by_time.items()):
            if len(tasks) > 1:
                names = ", ".join(
                    f"{self.owner.pet_for(t).name}: {t.description}" for t in tasks
                )
                warnings.append(f"Conflict at {time}: {names}")
        return warnings

    def busy_commitment(self, task: Task) -> Optional[Commitment]:
        """Return the owner's commitment that overlaps the task time, if any."""
        for commitment in self.owner.commitments:
            if commitment.overlaps(task.time):
                return commitment
        return None

    def get_reminders(self, now: Optional[datetime] = None) -> List[Task]:
        """Return today's not-yet-done tasks whose time has already arrived."""
        now = now or datetime.now()
        current = now.strftime("%H:%M")
        return [
            t
            for t in self.build_daily_plan(now.date())
            if t.time <= current and not t.completed
        ]
