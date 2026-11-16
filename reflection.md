# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core actions a user should be able to perform:

1. **Log medicine and feeding times.** The user can record when a pet was given medication or fed, so they can see what has already been done today and avoid missed or double doses and meals.
2. **Schedule a walk.** The user can plan a walk for a pet at a chosen date and time, and see it alongside the pet's other tasks.
3. **Schedule and view appointments.** The user can add upcoming appointments (for example, vet visits) for a pet and see them in a list of what is coming up.

- Briefly describe your initial UML design.

  The initial UML design centers on an Owner who has one or more Pets. Each Pet has its own Tasks (medicine, feeding, walks, appointments), and a Scheduler organizes those tasks into a daily plan across all of the owner's pets.

- What classes did you include, and what responsibilities did you assign to each?

  - **Owner:** Represents the user. Holds the owner's name, their list of pets, and their commitments, and is the entry point for adding a pet or a commitment.
  - **Commitment:** One block of time the owner is busy, such as work (a label, a start time, and an end time). An owner can have several. This is the simple alternative to connecting Google Calendar.
  - **Pet:** Represents one animal (name, species). Holds that pet's list of tasks and is responsible for adding tasks to itself.
  - **Task:** Represents a single care activity, such as a medicine dose, a feeding, a walk, or an appointment. Stores a description, type, time, and priority. Daily tasks like medicine keep a set of dates they were done, so each day just gets a tick.
  - **Scheduler:** Gathers tasks from all of an owner's pets and builds the daily plan. It sorts them by priority and time (i.e. a vet appointment is more important than a grooming appointment), works around the owner's commitments, shows today's tasks, lists upcoming walks and appointments, and returns a simple list of reminders for tasks that are due. Reminders are shown in the app, not pushed as real phone notifications.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

  Yes. `Owner` gained `get_all_tasks()` so the Scheduler reads every pet's tasks from one place instead of looping over pets itself. `Task` gained a `due_date` and `occurs_on()`, because the first design had no way to say which day a one-off task (like a vet visit) belongs to. I also renamed `mark_done` to `mark_complete` to match the project spec, and used `HH:MM` strings for times so sorting is just string order.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

  The scheduler considers three constraints: priority (high, medium, low), time of day, and the owner's commitments (busy blocks like work). Priority matters most, so a vet visit or medicine always comes before a low-priority walk or grooming, and time only breaks ties. I put the owner's commitments next: they don't remove a task, but the task gets a warning so the owner can decide what to do. I chose this order because missing medicine or an appointment is worse than doing a walk a bit late.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

  Conflict detection only checks for the exact same start time (for example two tasks at 10:00). It does not look at how long tasks take, so a 30-minute walk at 10:00 and a task at 10:15 are not flagged. This is reasonable here because tasks have no durations to keep the app simple for a busy owner, and a warning (not a block) is enough for them to adjust. Times are `HH:MM` strings, which keeps sorting trivial but means no validation of odd values.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

  I used Claude Code in VS Code for design brainstorming, generating the UML, writing the class skeleton and logic, wiring the Streamlit app, and writing tests. The most helpful prompts gave a concrete requirement and let the AI ask me decisions, for example "medicine should just get a tick each day, and add a way to enter work hours instead of Google Calendar." Splitting the project into two halves, with a commit after each, also kept the work organized and reviewable.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

  The AI's first design kept a daily task as one task with a set of done dates, which was simple but did not create a new task for the next day as the project requires. I chose to switch to a `frequency` field where completing a task creates the next one. I also did not accept connecting Google Calendar; I chose simple commitment blocks because it is much less complex. I verified results by running `python main.py`, running `python -m pytest` (13 passing), and reading the generated output. While testing, the AI found a bug where `pet_for()` matched tasks by value, so two identical tasks on different pets would be assigned to the wrong pet, and it was fixed to compare by identity.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

  I tested 13 behaviors: completing a task, adding a task to a pet, sorting by time, priority-before-time ordering, daily and weekly recurrence (and that one-off tasks don't recur), conflict detection (including no false alarm), a pet with no tasks, filtering by pet and status, busy-time flags, and reminders. These matter because the scheduler is the core of the app, and recurrence and conflicts are easy to get subtly wrong.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

  About 4 out of 5. The main behaviors and edge cases pass. Next I would test tasks that cross midnight, invalid time input, overlapping (not identical) times, and a recurring task completed late (after its due date).

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

  The scheduler: priority-first ordering that also warns when a task falls inside the owner's work hours, plus conflict warnings and recurring tasks, all verified by tests and a demo script.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

  I would add task durations so conflicts can detect overlapping times, save data to a file so pets and tasks persist between runs, and validate time input.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

  As the lead architect, my job was making the decisions (what to keep simple, what a "recurring task" means) while the AI wrote the code. Small, clear requirements and checking the output with tests worked much better than accepting the first version.
