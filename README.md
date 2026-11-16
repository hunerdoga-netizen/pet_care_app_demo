# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🧩 Implementation Summary

All logic lives in `pawpal_system.py`; `main.py` is a terminal demo and `app.py` is the Streamlit UI.

- `Task` (dataclass): description, type, time (`HH:MM`), priority, frequency (`once`/`daily`/`weekly`), due date and a completed flag. `mark_complete()` ticks it and returns the next occurrence if it repeats.
- `Pet` (dataclass): name, species and its list of tasks.
- `Commitment` (dataclass): a busy block (label, start, end) for the owner, e.g. work hours.
- `Owner` (dataclass): pets and commitments. `get_all_tasks()` returns every pet's tasks together.
- `Scheduler`: reads from `Owner.get_all_tasks()`, builds the daily plan (priority first, then time), sorts, filters, detects conflicts, creates recurring tasks, flags tasks that land in a commitment, and returns due reminders.
- `app.py` keeps the `Owner` in `st.session_state` so data survives Streamlit reruns.

## 🖥️ Sample Output

Output of `python main.py`. The first table is the daily plan (high priority first, then time). `[x]` marks a completed task, and `! owner busy` flags a task inside the owner's work hours. The script then shows sorting by time, a conflict warning, completing a daily task (which creates tomorrow's), and filtering.

```
Today's Schedule for Jordan (2026-11-16)
--------------------------------------------------------------
[ ] 08:00  Mochi   Joint medicine     high  
[ ] 10:00  Mochi   Vet appointment    high    ! owner busy: Work
[ ] 07:30  Mochi   Morning walk       medium
[ ] 07:45  Luna    Breakfast          medium
[ ] 18:00  Luna    Evening feeding    medium
[ ] 10:00  Luna    Grooming           low     ! owner busy: Work

Sorted by time only:
  07:30  Mochi   Morning walk
  07:45  Luna    Breakfast
  08:00  Mochi   Joint medicine
  10:00  Mochi   Vet appointment
  10:00  Luna    Grooming
  18:00  Luna    Evening feeding

Conflict warnings:
  ! Conflict at 10:00: Mochi: Vet appointment, Luna: Grooming

Completed 'Joint medicine'; next due 2026-11-17

Incomplete tasks for Mochi:
  2026-11-16 07:30  Morning walk
  2026-11-16 10:00  Vet appointment
  2026-11-17 08:00  Joint medicine

Today's Schedule for Jordan (2026-11-16)
--------------------------------------------------------------
[x] 08:00  Mochi   Joint medicine     high  
[ ] 10:00  Mochi   Vet appointment    high    ! owner busy: Work
[ ] 07:30  Mochi   Morning walk       medium
[ ] 07:45  Luna    Breakfast          medium
[ ] 18:00  Luna    Evening feeding    medium
[ ] 10:00  Luna    Grooming           low     ! owner busy: Work
```

## 🧪 Testing PawPal+

```bash
python -m pytest
```

The 13 tests in `tests/test_pawpal.py` cover: marking a task complete, adding a task to a pet, sorting by time, priority-before-time ordering, daily and weekly recurrence (and one-off tasks not recurring), conflict detection (same time across pets, and no false positives), a pet with no tasks, filtering by pet and status, commitment (busy time) flags, and reminders.

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/dogahuner/codepath/pet_care_app_demo
collected 13 items

tests/test_pawpal.py .............                                       [100%]

============================== 13 passed in 0.01s ==============================
```

**Confidence level:** ⭐⭐⭐⭐ (4/5). The core behaviors and the main edge cases pass. Not yet tested: tasks that span midnight, invalid time strings, and overlapping (not just identical) times.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.build_daily_plan()` | `sort_by_time` orders by `HH:MM`; the daily plan orders by priority (high, medium, low) and then time |
| Filtering | `Scheduler.filter_tasks()` | Filter by pet name and/or completion status |
| Conflict handling | `Scheduler.detect_conflicts()` | Returns warning strings when two tasks share the exact same time on a day (same or different pets). It never crashes or blocks adding a task |
| Recurring tasks | `Task.mark_complete()`, `Scheduler.mark_task_complete()` | Completing a daily/weekly task adds a new copy due +1 day / +7 days (`timedelta`) |
| Busy-time check | `Scheduler.busy_commitment()` | Flags a task that falls inside one of the owner's commitments (e.g. work) |
| Reminders | `Scheduler.get_reminders()` | Today's tasks that are due and not done, shown in the app |

## ✨ Features

- Add an owner, several pets, and tasks (walk, medicine, feeding, appointment)
- Priority-first daily plan with a time tiebreak
- Sorting by time and filtering by pet or status
- Conflict warnings for tasks at the same time
- Daily and weekly recurrence that creates the next task automatically
- Owner commitments (work hours) with a busy warning on affected tasks
- In-app "due now" reminders

## 📸 Demo Walkthrough

1. Start the app with `streamlit run app.py`. Enter your name, and optionally add busy times such as Work 09:00–17:00 under "Busy times".
2. Add a pet (name and species). Add as many pets as you like.
3. Add tasks for a pet: description, type, time, priority and how often it repeats (once, daily, weekly). For example, a daily high-priority "Joint medicine" at 08:00 and a one-off "Vet appointment" at 10:00.
4. Look at **Today's schedule**. Tasks are ordered high priority first, then by time. A task inside your busy time shows a "you're busy" note, and two tasks at the same time trigger a yellow conflict warning.
5. Tick a task to complete it. If it repeats, tomorrow's copy is created automatically. When every task is done you see a success message, and tasks that are due and not done show up under "Due now".
6. Use **All tasks** to filter by pet and status.

**Key Scheduler behaviors shown:** priority-then-time ordering, conflict warnings, recurrence, busy-time flags, filtering.

**CLI output** (`python main.py`):

```
Today's Schedule for Jordan (2026-11-16)
--------------------------------------------------------------
[ ] 08:00  Mochi   Joint medicine     high  
[ ] 10:00  Mochi   Vet appointment    high    ! owner busy: Work
[ ] 07:30  Mochi   Morning walk       medium
[ ] 07:45  Luna    Breakfast          medium
[ ] 18:00  Luna    Evening feeding    medium
[ ] 10:00  Luna    Grooming           low     ! owner busy: Work

Sorted by time only:
  07:30  Mochi   Morning walk
  07:45  Luna    Breakfast
  08:00  Mochi   Joint medicine
  10:00  Mochi   Vet appointment
  10:00  Luna    Grooming
  18:00  Luna    Evening feeding

Conflict warnings:
  ! Conflict at 10:00: Mochi: Vet appointment, Luna: Grooming

Completed 'Joint medicine'; next due 2026-11-17

Incomplete tasks for Mochi:
  2026-11-16 07:30  Morning walk
  2026-11-16 10:00  Vet appointment
  2026-11-17 08:00  Joint medicine

Today's Schedule for Jordan (2026-11-16)
--------------------------------------------------------------
[x] 08:00  Mochi   Joint medicine     high  
[ ] 10:00  Mochi   Vet appointment    high    ! owner busy: Work
[ ] 07:30  Mochi   Morning walk       medium
[ ] 07:45  Luna    Breakfast          medium
[ ] 18:00  Luna    Evening feeding    medium
[ ] 10:00  Luna    Grooming           low     ! owner busy: Work
```

**Screenshot or video** *(optional)*: 
