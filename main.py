from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner("Jordan")

mochi = Pet("Mochi", "dog")
whiskers = Pet("Whiskers", "cat")

owner.add_pet(mochi)
owner.add_pet(whiskers)

mochi.add_task(Task("Morning walk", "08:00", "daily"))
mochi.add_task(Task("Evening walk", "18:00", "daily"))
whiskers.add_task(Task("Feeding", "07:30", "daily"))

scheduler = Scheduler(owner)

print("Today's Schedule")
print("-" * 20)
for task in scheduler.organize_by_time():
    print(f"{task.time} — {task.description}")
