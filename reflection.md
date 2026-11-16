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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
