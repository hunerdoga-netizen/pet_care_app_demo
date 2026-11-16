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
        tick = "[x]" if task.is_done(day) else "[ ]"
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
    mochi.add_task(Task("Joint medicine", "medicine", "08:00", "high", daily=True))
    mochi.add_task(Task("Vet appointment", "appointment", "10:00", "high"))
    luna.add_task(Task("Breakfast", "feeding", "07:45", "medium", daily=True))
    luna.add_task(Task("Evening feeding", "feeding", "18:00", "medium", daily=True))

    # Tick today's medicine, like checking it off in the app.
    mochi.tasks[1].mark_complete(today)

    scheduler = Scheduler(owner)
    print_schedule(scheduler, today)


if __name__ == "__main__":
    main()
