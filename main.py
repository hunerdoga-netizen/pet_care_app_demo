"""Terminal demo for the PawPal+ logic layer."""

from datetime import date

from pawpal_system import Commitment, Owner, Pet, Scheduler, Task


def print_schedule(scheduler: Scheduler, day: date) -> None:
    """Print the day's plan in a readable table."""
    owner = scheduler.owner
    print(f"Today's Schedule for {owner.name} ({day.isoformat()})")
    print("-" * 62)
    for task in scheduler.build_daily_plan(day):
        pet = owner.pet_for(task)
        tick = "[x]" if task.completed else "[ ]"
        line = (
            f"{tick} {task.time}  {pet.name:<7} {task.description:<18} "
            f"{task.priority:<6}"
        )
        busy = scheduler.busy_commitment(task)
        if busy:
            line += f"  ! owner busy: {busy.label}"
        print(line)


def main() -> None:
    owner = Owner("Jordan")
    owner.add_commitment(Commitment("Work", "09:00", "17:00"))

    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    today = date.today()
    mochi.add_task(Task("Morning walk", "walk", "07:30", "medium"))
    mochi.add_task(Task("Joint medicine", "medicine", "08:00", "high", "daily"))
    mochi.add_task(Task("Vet appointment", "appointment", "10:00", "high"))
    luna.add_task(Task("Breakfast", "feeding", "07:45", "medium", "daily"))
    luna.add_task(Task("Evening feeding", "feeding", "18:00", "medium", "daily"))

    # Added out of order on purpose, and at the same time as Mochi's vet visit.
    luna.add_task(Task("Grooming", "appointment", "10:00", "low"))

    scheduler = Scheduler(owner)
    print_schedule(scheduler, today)

    print("\nSorted by time only:")
    for t in scheduler.sort_by_time(scheduler.get_tasks_for(today)):
        print(f"  {t.time}  {owner.pet_for(t).name:<7} {t.description}")

    print("\nConflict warnings:")
    for warning in scheduler.detect_conflicts(today):
        print(f"  ! {warning}")

    # Complete the daily medicine: a new one is created for tomorrow.
    medicine = mochi.tasks[1]
    next_task = scheduler.mark_task_complete(medicine)
    print(f"\nCompleted '{medicine.description}'; next due {next_task.due_date}")
    print("\nIncomplete tasks for Mochi:")
    for t in scheduler.filter_tasks(pet_name="Mochi", completed=False):
        print(f"  {t.due_date} {t.time}  {t.description}")

    print()
    print_schedule(scheduler, today)


if __name__ == "__main__":
    main()
