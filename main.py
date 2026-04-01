from pawpal_system import Owner, Pet, Scheduler, Task

import importlib

try:
    tabulate_module = importlib.import_module("tabulate")
    tabulate = tabulate_module.tabulate
except ImportError:  # pragma: no cover
    tabulate = None


def print_schedule(title: str, schedule: list[tuple[Pet, Task]]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    if not schedule:
        print("No tasks found.")
        return

    rows = []
    for pet, task in schedule:
        rows.append(
            [
                pet.name,
                task.description,
                task.due_date.isoformat(),
                task.time,
                task.priority,
                task.frequency,
                "done" if task.completed else "pending",
            ]
        )

    headers = ["Pet", "Task", "Date", "Time", "Priority", "Frequency", "Status"]
    if tabulate:
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
    else:
        for row in rows:
            print(" | ".join(str(item) for item in row))


def print_time_blocked_plan(title: str, plan_rows: list[dict[str, object]]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    if not plan_rows:
        print("No plan rows.")
        return

    headers = ["pet", "task", "date", "original_time", "planned_time", "priority", "duration_minutes"]
    rows = [[row[h] for h in headers] for row in plan_rows]
    if tabulate:
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
    else:
        for row in rows:
            print(" | ".join(str(item) for item in row))


def run_demo() -> None:
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Add tasks out of order to demonstrate sorting.
    mochi.add_task(Task(description="Evening walk", time="19:00", priority="high", frequency="daily"))
    mochi.add_task(Task(description="Morning feed", time="08:00", priority="high"))
    luna.add_task(Task(description="Medication", time="08:00", priority="high", frequency="weekly"))
    luna.add_task(Task(description="Play time", time="18:30", priority="medium"))

    scheduler = Scheduler(owner)

    full_schedule = scheduler.get_schedule(include_completed=False)
    print_schedule("Today's Schedule (Sorted)", full_schedule)

    pending_mochi = scheduler.filter_tasks(full_schedule, pet_name="Mochi", completed=False)
    print_schedule("Filtered: Mochi Pending", pending_mochi)

    conflicts = scheduler.detect_conflicts(full_schedule)
    print("\nConflict Check")
    print("--------------")
    if conflicts:
        for warning in conflicts:
            print(f"WARNING: {warning}")
    else:
        print("No conflicts found.")

    # Demonstrate recurrence generation.
    print("\nMarking Mochi's first task complete...")
    scheduler.mark_task_complete("Mochi", 0)
    updated_schedule = scheduler.get_schedule(include_completed=True)
    print_schedule("Updated Schedule (with completed + recurrence)", updated_schedule)

    weighted = scheduler.sort_by_priority_then_time()
    print_schedule("Weighted Priority Schedule", weighted)

    time_blocked_plan, plan_warnings = scheduler.generate_time_blocked_plan()
    print_time_blocked_plan("Time-Blocked Non-Overlapping Plan", time_blocked_plan)
    if plan_warnings:
        print("\nPlan Adjustments")
        print("----------------")
        for warning in plan_warnings:
            print(f"INFO: {warning}")

    next_slot = scheduler.next_available_slot(target_date=updated_schedule[0][1].due_date, duration_minutes=45)
    print("\nNext Available Slot")
    print("-------------------")
    print(next_slot if next_slot else "No available slot")


if __name__ == "__main__":
    run_demo()
