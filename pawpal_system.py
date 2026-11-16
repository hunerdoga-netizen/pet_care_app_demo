"""PawPal+ logic layer: Owner, Commitment, Pet, Task and Scheduler."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional, Set

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
    daily: bool = False
    due_date: date = field(default_factory=date.today)
    done_dates: Set[date] = field(default_factory=set)

    def occurs_on(self, day: date) -> bool:
        """Return True if this task is scheduled for the given day."""
        if self.daily:
            return day >= self.due_date
        return day == self.due_date

    def mark_complete(self, day: Optional[date] = None) -> None:
        """Tick this task as done for the given day (default: today)."""
        self.done_dates.add(day or date.today())

    def is_done(self, day: Optional[date] = None) -> bool:
        """Return True if this task has been ticked for the given day."""
        return (day or date.today()) in self.done_dates


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
            if task in pet.tasks:
                return pet
        return None


class Scheduler:
    """The brain: builds the daily plan from all of an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def get_tasks_for(self, day: date) -> List[Task]:
        """Return all tasks (across all pets) that occur on the given day."""
        return [t for t in self.owner.get_all_tasks() if t.occurs_on(day)]

    def build_daily_plan(self, day: date) -> List[Task]:
        """Return the day's tasks ordered by priority (high first), then time."""
        return sorted(
            self.get_tasks_for(day),
            key=lambda t: (PRIORITY_ORDER.get(t.priority, 1), t.time),
        )

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
            if t.time <= current and not t.is_done(now.date())
        ]
