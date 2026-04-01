from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


PRIORITY_ORDER: Dict[str, int] = {"high": 0, "medium": 1, "low": 2}
PRIORITY_SCORE: Dict[str, int] = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Task:
    """A single care task for a pet."""

    description: str
    time: str
    frequency: str = "once"
    priority: str = "medium"
    duration_minutes: int = 15
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as complete."""
        self.completed = True

    def to_dict(self) -> Dict[str, str | int | bool]:
        """Convert task to a JSON-safe dictionary."""
        return {
            "description": self.description,
            "time": self.time,
            "frequency": self.frequency,
            "priority": self.priority,
            "duration_minutes": self.duration_minutes,
            "due_date": self.due_date.isoformat(),
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str | int | bool]) -> "Task":
        """Create a Task from a dictionary."""
        return cls(
            description=str(data["description"]),
            time=str(data["time"]),
            frequency=str(data.get("frequency", "once")),
            priority=str(data.get("priority", "medium")),
            duration_minutes=int(data.get("duration_minutes", 15)),
            due_date=date.fromisoformat(str(data.get("due_date", date.today().isoformat()))),
            completed=bool(data.get("completed", False)),
        )


@dataclass
class Pet:
    """A pet and its scheduled tasks."""

    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        self.tasks.append(task)

    def pending_tasks(self) -> List[Task]:
        """Return all incomplete tasks for this pet."""
        return [task for task in self.tasks if not task.completed]

    def to_dict(self) -> Dict[str, object]:
        """Convert pet to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Pet":
        """Create a Pet from a dictionary."""
        raw_tasks = data.get("tasks", [])
        task_items = raw_tasks if isinstance(raw_tasks, list) else []
        tasks = [Task.from_dict(task_data) for task_data in task_items if isinstance(task_data, dict)]
        return cls(
            name=str(data["name"]),
            species=str(data.get("species", "other")),
            tasks=tasks,
        )


@dataclass
class Owner:
    """A pet owner with one or more pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet if it does not already exist by name."""
        if self.get_pet(pet.name) is None:
            self.pets.append(pet)

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Find a pet by case-insensitive name."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet
        return None

    def get_all_tasks(self, include_completed: bool = True) -> List[Tuple[Pet, Task]]:
        """Return all tasks paired with their pet."""
        records: List[Tuple[Pet, Task]] = []
        for pet in self.pets:
            for task in pet.tasks:
                if include_completed or not task.completed:
                    records.append((pet, task))
        return records

    def to_dict(self) -> Dict[str, object]:
        """Convert owner data to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "pets": [pet.to_dict() for pet in self.pets],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Owner":
        """Create an Owner from a dictionary."""
        raw_pets = data.get("pets", [])
        pet_items = raw_pets if isinstance(raw_pets, list) else []
        pets = [Pet.from_dict(item) for item in pet_items if isinstance(item, dict)]
        return cls(name=str(data.get("name", "Owner")), pets=pets)

    def save_to_json(self, file_path: str) -> None:
        """Save owner, pets, and tasks to a JSON file."""
        path = Path(file_path)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_from_json(cls, file_path: str) -> "Owner":
        """Load owner data from a JSON file, or return an empty owner if missing."""
        path = Path(file_path)
        if not path.exists():
            return cls(name="Jordan")

        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return cls.from_dict(payload)
        return cls(name="Jordan")


class Scheduler:
    """Scheduling and algorithmic operations for all owner tasks."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def _time_key(self, task: Task) -> datetime:
        return datetime.strptime(task.time, "%H:%M")

    def _end_time(self, task: Task) -> datetime:
        return self._time_key(task) + timedelta(minutes=task.duration_minutes)

    def get_schedule(self, include_completed: bool = False) -> List[Tuple[Pet, Task]]:
        """Get all tasks sorted by due date, time, then priority."""
        records = self.owner.get_all_tasks(include_completed=include_completed)
        return sorted(
            records,
            key=lambda record: (
                record[1].due_date,
                self._time_key(record[1]),
                PRIORITY_ORDER.get(record[1].priority.lower(), 99),
            ),
        )

    def sort_by_time(self, records: List[Tuple[Pet, Task]]) -> List[Tuple[Pet, Task]]:
        """Sort a provided task list by date, time, and priority."""
        return sorted(
            records,
            key=lambda record: (
                record[1].due_date,
                self._time_key(record[1]),
                PRIORITY_ORDER.get(record[1].priority.lower(), 99),
            ),
        )

    def sort_by_priority_then_time(
        self,
        records: Optional[List[Tuple[Pet, Task]]] = None,
    ) -> List[Tuple[Pet, Task]]:
        """Sort tasks by weighted priority first, then by date and time."""
        source = records if records is not None else self.owner.get_all_tasks(include_completed=False)
        return sorted(
            source,
            key=lambda record: (
                -PRIORITY_SCORE.get(record[1].priority.lower(), 0),
                record[1].due_date,
                self._time_key(record[1]),
            ),
        )

    def filter_tasks(
        self,
        records: Optional[List[Tuple[Pet, Task]]] = None,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Tuple[Pet, Task]]:
        """Filter tasks by pet name and/or completion status."""
        source = records if records is not None else self.owner.get_all_tasks(include_completed=True)
        filtered = source

        if pet_name:
            filtered = [
                (pet, task) for (pet, task) in filtered if pet.name.lower() == pet_name.lower()
            ]

        if completed is not None:
            filtered = [(pet, task) for (pet, task) in filtered if task.completed is completed]

        return filtered

    def detect_conflicts(
        self,
        records: Optional[List[Tuple[Pet, Task]]] = None,
    ) -> List[str]:
        """Return warnings for tasks that share the exact same date and time."""
        source = records if records is not None else self.owner.get_all_tasks(include_completed=False)
        buckets: Dict[Tuple[date, str], List[Tuple[Pet, Task]]] = {}
        for pet, task in source:
            key = (task.due_date, task.time)
            buckets.setdefault(key, []).append((pet, task))

        warnings: List[str] = []
        for (task_date, task_time), matches in buckets.items():
            if len(matches) > 1:
                names = ", ".join(f"{pet.name}: {task.description}" for pet, task in matches)
                warnings.append(
                    f"Conflict at {task_time} on {task_date.isoformat()} -> {names}"
                )

        return warnings

    def detect_time_overlap_conflicts(
        self,
        records: Optional[List[Tuple[Pet, Task]]] = None,
    ) -> List[str]:
        """Detect overlapping tasks by comparing start/end windows across all pets."""
        source = records if records is not None else self.owner.get_all_tasks(include_completed=False)
        grouped: Dict[date, List[Tuple[Pet, Task]]] = {}
        for pet, task in source:
            grouped.setdefault(task.due_date, []).append((pet, task))

        warnings: List[str] = []
        for task_date, day_records in grouped.items():
            ordered = sorted(day_records, key=lambda item: self._time_key(item[1]))
            for i in range(len(ordered)):
                pet_a, task_a = ordered[i]
                start_a = self._time_key(task_a)
                end_a = self._end_time(task_a)
                for j in range(i + 1, len(ordered)):
                    pet_b, task_b = ordered[j]
                    start_b = self._time_key(task_b)
                    end_b = self._end_time(task_b)
                    if start_b < end_a and start_a < end_b:
                        warnings.append(
                            "Overlap on "
                            f"{task_date.isoformat()} between "
                            f"{pet_a.name}: {task_a.description} ({task_a.time}) and "
                            f"{pet_b.name}: {task_b.description} ({task_b.time})"
                        )
        return warnings

    def next_available_slot(
        self,
        target_date: date,
        duration_minutes: int,
        start_time: str = "06:00",
        end_time: str = "22:00",
        records: Optional[List[Tuple[Pet, Task]]] = None,
    ) -> Optional[str]:
        """Find the next available non-overlapping slot in 15-minute increments."""
        source = records if records is not None else self.owner.get_all_tasks(include_completed=False)
        day_records = [(pet, task) for pet, task in source if task.due_date == target_date]

        slot = datetime.strptime(start_time, "%H:%M")
        day_end = datetime.strptime(end_time, "%H:%M")
        step = timedelta(minutes=15)
        requested = timedelta(minutes=duration_minutes)

        while slot + requested <= day_end:
            slot_end = slot + requested
            has_overlap = False
            for _, task in day_records:
                task_start = self._time_key(task)
                task_end = self._end_time(task)
                if slot < task_end and task_start < slot_end:
                    has_overlap = True
                    break

            if not has_overlap:
                return slot.strftime("%H:%M")
            slot += step

        return None

    def generate_time_blocked_plan(
        self,
        records: Optional[List[Tuple[Pet, Task]]] = None,
    ) -> Tuple[List[Dict[str, object]], List[str]]:
        """Build a plan that preserves priority while shifting overlapping tasks."""
        source = records if records is not None else self.owner.get_all_tasks(include_completed=False)
        ordered = self.sort_by_priority_then_time(source)

        planned: List[Dict[str, object]] = []
        warnings: List[str] = []

        # Tracks already allocated windows by date.
        allocations: Dict[date, List[Tuple[datetime, datetime]]] = {}

        for pet, task in ordered:
            original_start = self._time_key(task)
            task_len = timedelta(minutes=task.duration_minutes)
            day_allocations = allocations.setdefault(task.due_date, [])

            chosen_start = original_start
            chosen_end = chosen_start + task_len

            def overlaps_existing(start: datetime, end: datetime) -> bool:
                for used_start, used_end in day_allocations:
                    if start < used_end and used_start < end:
                        return True
                return False

            while overlaps_existing(chosen_start, chosen_end):
                chosen_start += timedelta(minutes=15)
                chosen_end = chosen_start + task_len

            if chosen_start.strftime("%H:%M") != task.time:
                warnings.append(
                    f"Rescheduled {pet.name}: {task.description} from {task.time} to {chosen_start.strftime('%H:%M')}"
                )

            day_allocations.append((chosen_start, chosen_end))

            planned.append(
                {
                    "pet": pet.name,
                    "task": task.description,
                    "date": task.due_date.isoformat(),
                    "original_time": task.time,
                    "planned_time": chosen_start.strftime("%H:%M"),
                    "priority": task.priority,
                    "duration_minutes": task.duration_minutes,
                }
            )

        return planned, warnings

    def mark_task_complete(self, pet_name: str, task_index: int) -> Task:
        """Mark a task complete and auto-generate the next recurring task if needed."""
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            raise ValueError(f"Pet '{pet_name}' not found")

        if task_index < 0 or task_index >= len(pet.tasks):
            raise IndexError("Task index out of range")

        task = pet.tasks[task_index]
        task.mark_complete()

        recurrence_days = {"daily": 1, "weekly": 7}
        freq = task.frequency.lower()
        if freq in recurrence_days:
            next_task = Task(
                description=task.description,
                time=task.time,
                frequency=task.frequency,
                priority=task.priority,
                duration_minutes=task.duration_minutes,
                due_date=task.due_date + timedelta(days=recurrence_days[freq]),
                completed=False,
            )
            pet.add_task(next_task)

        return task
