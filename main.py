from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner("Jordan")

mochi = Pet("Mochi", "dog")
whiskers = Pet("Whiskers", "cat")

owner.add_pet(mochi)
owner.add_pet(whiskers)

# Added out of order on purpose to verify sorting works.
mochi.add_task(Task("Evening walk", "18:00", "daily"))
whiskers.add_task(Task("Feeding", "07:30", "daily"))
mochi.add_task(Task("Vet checkup", "10:00", "once"))
mochi.add_task(Task("Morning walk", "08:00", "daily"))
whiskers.add_task(Task("Litter cleaning", "12:00", "daily"))

# Same start time as Mochi's "Morning walk" on purpose, to verify conflict detection works.
whiskers.add_task(Task("Morning brushing", "08:00", "daily"))

scheduler = Scheduler(owner)

# Complete one task via the scheduler so its next occurrence is scheduled automatically.
scheduler.complete_task(mochi.get_tasks()[0])

print("Today's Schedule (sorted by time)")
print("-" * 35)
for task in scheduler.organize_by_time():
    print(f"{task.time} — {task.description} ({task.frequency})")

print()
print("Pending Tasks")
print("-" * 35)
for task in scheduler.filter_tasks(status="pending"):
    print(f"{task.time} — {task.description}")

print()
print("Completed Tasks")
print("-" * 35)
for task in scheduler.filter_tasks(status="completed"):
    print(f"{task.time} — {task.description}")

print()
print("Mochi's Tasks")
print("-" * 35)
for task in scheduler.filter_tasks(pet_name="Mochi"):
    print(f"{task.time} — {task.description}")

print()
print("Mochi's Pending Tasks")
print("-" * 35)
for task in scheduler.filter_tasks(pet_name="Mochi", status="pending"):
    print(f"{task.time} — {task.description}")

print()
print("Conflict Check")
print("-" * 35)
conflict_warning = scheduler.check_for_conflicts()
print(conflict_warning if conflict_warning else "No conflicts found.")
