from datetime import date, timedelta
from pathlib import Path

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_updates_status() -> None:
    task = Task(description="Walk", time="09:00")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_to_pet_increases_count() -> None:
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task(description="Feed", time="08:00"))

    assert len(pet.tasks) == 1


def test_sorting_returns_chronological_order() -> None:
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task(description="Late", time="18:00"))
    pet.add_task(Task(description="Early", time="07:30"))

    scheduler = Scheduler(owner)
    schedule = scheduler.get_schedule()

    assert [task.description for _, task in schedule] == ["Early", "Late"]


def test_daily_recurrence_creates_next_task() -> None:
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)

    today_task = Task(
        description="Evening walk",
        time="19:00",
        frequency="daily",
        due_date=date.today(),
    )
    pet.add_task(today_task)

    scheduler = Scheduler(owner)
    scheduler.mark_task_complete("Mochi", 0)

    assert len(pet.tasks) == 2
    assert pet.tasks[0].completed is True
    assert pet.tasks[1].due_date == date.today() + timedelta(days=1)
    assert pet.tasks[1].completed is False


def test_conflict_detection_flags_duplicate_times() -> None:
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task(description="Walk", time="08:00"))
    luna.add_task(Task(description="Medication", time="08:00"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "Conflict at 08:00" in conflicts[0]


def test_overlap_conflict_detection_uses_duration() -> None:
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task(description="Long walk", time="08:00", duration_minutes=60))
    luna.add_task(Task(description="Vet prep", time="08:30", duration_minutes=30))

    scheduler = Scheduler(owner)
    overlap_warnings = scheduler.detect_time_overlap_conflicts()

    assert len(overlap_warnings) == 1
    assert "Overlap on" in overlap_warnings[0]


def test_next_available_slot_skips_conflict_window() -> None:
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task(description="Walk", time="08:00", duration_minutes=60))

    scheduler = Scheduler(owner)
    slot = scheduler.next_available_slot(
        target_date=date.today(),
        duration_minutes=30,
        start_time="08:00",
    )

    assert slot == "09:00"


def test_owner_save_and_load_json_round_trip() -> None:
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task(description="Feed", time="08:00", priority="high"))

    temp_path = Path("tests_tmp_owner.json")
    try:
        owner.save_to_json(str(temp_path))
        loaded = Owner.load_from_json(str(temp_path))
    finally:
        if temp_path.exists():
            temp_path.unlink()

    assert loaded.name == "Jordan"
    assert len(loaded.pets) == 1
    assert loaded.pets[0].name == "Mochi"
    assert loaded.pets[0].tasks[0].description == "Feed"
