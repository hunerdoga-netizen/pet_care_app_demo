from datetime import date, datetime, timedelta

from pawpal_system import Commitment, Owner, Pet, Scheduler, Task

TODAY = date(2026, 11, 16)


def make_scheduler():
    owner = Owner("Jordan")
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    return owner, mochi, luna, Scheduler(owner)


def test_mark_complete_changes_status():
    task = Task("Medicine", "medicine", "08:00")
    assert not task.completed
    task.mark_complete()
    assert task.completed


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", "walk", "07:30"))
    assert len(pet.tasks) == 1


def test_sort_by_time_is_chronological():
    _, mochi, luna, sched = make_scheduler()
    mochi.add_task(Task("Dinner", "feeding", "18:00", due_date=TODAY))
    luna.add_task(Task("Breakfast", "feeding", "07:45", due_date=TODAY))
    mochi.add_task(Task("Walk", "walk", "12:30", due_date=TODAY))
    times = [t.time for t in sched.sort_by_time(sched.get_tasks_for(TODAY))]
    assert times == ["07:45", "12:30", "18:00"]


def test_plan_orders_priority_before_time():
    _, mochi, _, sched = make_scheduler()
    mochi.add_task(Task("Walk", "walk", "07:00", "low", due_date=TODAY))
    mochi.add_task(Task("Vet", "appointment", "15:00", "high", due_date=TODAY))
    assert [t.description for t in sched.build_daily_plan(TODAY)] == ["Vet", "Walk"]


def test_daily_task_creates_next_day_task():
    _, mochi, _, sched = make_scheduler()
    med = Task("Medicine", "medicine", "08:00", frequency="daily", due_date=TODAY)
    mochi.add_task(med)
    nxt = sched.mark_task_complete(med)
    assert med.completed
    assert nxt.due_date == TODAY + timedelta(days=1)
    assert not nxt.completed
    assert nxt in mochi.tasks


def test_weekly_task_creates_task_seven_days_later():
    _, mochi, _, sched = make_scheduler()
    bath = Task("Bath", "grooming", "10:00", frequency="weekly", due_date=TODAY)
    mochi.add_task(bath)
    assert sched.mark_task_complete(bath).due_date == TODAY + timedelta(days=7)


def test_one_off_task_does_not_recur():
    _, mochi, _, sched = make_scheduler()
    vet = Task("Vet", "appointment", "10:00", due_date=TODAY)
    mochi.add_task(vet)
    assert sched.mark_task_complete(vet) is None
    assert len(mochi.tasks) == 1


def test_conflict_detected_for_same_time_across_pets():
    _, mochi, luna, sched = make_scheduler()
    mochi.add_task(Task("Vet", "appointment", "10:00", due_date=TODAY))
    luna.add_task(Task("Grooming", "appointment", "10:00", due_date=TODAY))
    warnings = sched.detect_conflicts(TODAY)
    assert len(warnings) == 1 and "10:00" in warnings[0]


def test_no_conflict_when_times_differ():
    _, mochi, luna, sched = make_scheduler()
    mochi.add_task(Task("Vet", "appointment", "10:00", due_date=TODAY))
    luna.add_task(Task("Grooming", "appointment", "11:00", due_date=TODAY))
    assert sched.detect_conflicts(TODAY) == []


def test_pet_with_no_tasks_gives_empty_plan():
    _, _, _, sched = make_scheduler()
    assert sched.build_daily_plan(TODAY) == []


def test_filter_by_pet_and_status():
    _, mochi, luna, sched = make_scheduler()
    done = Task("Walk", "walk", "07:00", due_date=TODAY)
    done.mark_complete()
    mochi.add_task(done)
    mochi.add_task(Task("Dinner", "feeding", "18:00", due_date=TODAY))
    luna.add_task(Task("Breakfast", "feeding", "08:00", due_date=TODAY))
    assert [t.description for t in sched.filter_tasks("Mochi", completed=False)] == ["Dinner"]
    assert len(sched.filter_tasks("Luna")) == 1


def test_task_inside_commitment_is_flagged():
    owner, mochi, _, sched = make_scheduler()
    owner.add_commitment(Commitment("Work", "09:00", "17:00"))
    inside = Task("Vet", "appointment", "10:00", due_date=TODAY)
    outside = Task("Walk", "walk", "08:00", due_date=TODAY)
    mochi.add_task(inside)
    mochi.add_task(outside)
    assert sched.busy_commitment(inside).label == "Work"
    assert sched.busy_commitment(outside) is None


def test_reminders_only_include_due_incomplete_tasks():
    _, mochi, _, sched = make_scheduler()
    mochi.add_task(Task("Morning", "medicine", "08:00", due_date=TODAY))
    mochi.add_task(Task("Later", "walk", "20:00", due_date=TODAY))
    names = [t.description for t in sched.get_reminders(datetime(2026, 11, 16, 9, 0))]
    assert names == ["Morning"]
