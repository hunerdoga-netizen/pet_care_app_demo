from datetime import date, datetime

import streamlit as st

from pawpal_system import Commitment, Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# Streamlit reruns this script on every click, so keep the Owner in session_state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)
today = date.today()

# --- Owner ---
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

with st.expander("Busy times (work, commitments)"):
    c1, c2, c3 = st.columns(3)
    label = c1.text_input("Label", value="Work")
    start = c2.time_input("From", value=datetime.strptime("09:00", "%H:%M").time())
    end = c3.time_input("To", value=datetime.strptime("17:00", "%H:%M").time())
    if st.button("Add busy time"):
        owner.add_commitment(
            Commitment(label, start.strftime("%H:%M"), end.strftime("%H:%M"))
        )
    for c in owner.commitments:
        st.write(f"🕘 {c.label}: {c.start}–{c.end}")

# --- Pets ---
st.subheader("Pets")
p1, p2 = st.columns(2)
pet_name = p1.text_input("Pet name", value="Mochi")
species = p2.selectbox("Species", ["dog", "cat", "other"])
if st.button("Add pet"):
    owner.add_pet(Pet(pet_name, species))

if not owner.pets:
    st.info("No pets yet. Add one above.")
else:
    st.write("Your pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))

    # --- Tasks ---
    st.subheader("Add a task")
    pet_choice = st.selectbox("Pet", [p.name for p in owner.pets])
    t1, t2, t3, t4 = st.columns(4)
    description = t1.text_input("Task", value="Morning walk")
    task_type = t2.selectbox("Type", ["walk", "medicine", "feeding", "appointment"])
    task_time = t3.time_input("Time", value=datetime.strptime("08:00", "%H:%M").time())
    priority = t4.selectbox("Priority", ["high", "medium", "low"], index=1)
    frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
    if st.button("Add task"):
        pet = next(p for p in owner.pets if p.name == pet_choice)
        pet.add_task(
            Task(description, task_type, task_time.strftime("%H:%M"), priority, frequency)
        )

    # --- Today's schedule ---
    st.divider()
    st.subheader(f"Today's schedule ({today.isoformat()})")
    st.caption("High priority first, then by time.")

    for warning in scheduler.detect_conflicts(today):
        st.warning(f"⚠️ {warning}. Move one of these tasks to a different time.")

    plan = scheduler.build_daily_plan(today)
    if not plan:
        st.info("No tasks for today.")
    for task in plan:
        pet = owner.pet_for(task)
        done = st.checkbox(
            f"{task.time} · {pet.name} · {task.description} [{task.priority}]"
            + (f" · repeats {task.frequency}" if task.frequency != "once" else ""),
            value=task.completed,
            key=f"done-{id(task)}",
        )
        if done and not task.completed:
            scheduler.mark_task_complete(task)  # creates the next one if recurring
            st.rerun()
        busy = scheduler.busy_commitment(task)
        if busy:
            st.caption(f"⏳ You're busy ({busy.label}) at {task.time}.")

    if plan and all(t.completed for t in plan):
        st.success("All of today's tasks are done! 🎉")

    reminders = scheduler.get_reminders(datetime.now())
    if reminders:
        st.error("Due now: " + ", ".join(t.description for t in reminders))

    # --- Browse / filter all tasks ---
    st.divider()
    st.subheader("All tasks")
    f1, f2 = st.columns(2)
    pet_filter = f1.selectbox("Pet", ["All"] + [p.name for p in owner.pets])
    status_filter = f2.selectbox("Status", ["All", "Not done", "Done"])
    completed = {"All": None, "Not done": False, "Done": True}[status_filter]
    shown = scheduler.filter_tasks(
        None if pet_filter == "All" else pet_filter, completed
    )
    shown = sorted(shown, key=lambda t: (t.due_date, t.time))
    if shown:
        st.table(
            [
                {
                    "Date": t.due_date.isoformat(),
                    "Time": t.time,
                    "Pet": owner.pet_for(t).name,
                    "Task": t.description,
                    "Priority": t.priority,
                    "Repeats": t.frequency,
                    "Done": "✅" if t.completed else "",
                }
                for t in shown
            ]
        )
    else:
        st.info("No tasks match this filter.")
