from datetime import date

from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    task = Task("Joint medicine", "medicine", "08:00", daily=True)
    assert not task.is_done()
    task.mark_complete()
    assert task.is_done()


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Morning walk", "walk", "07:30"))
    assert len(pet.tasks) == 1


def test_daily_tick_is_per_day():
    task = Task("Medicine", "medicine", "08:00", daily=True, due_date=date(2026, 1, 1))
    task.mark_complete(date(2026, 1, 1))
    assert task.is_done(date(2026, 1, 1))
    assert not task.is_done(date(2026, 1, 2))
