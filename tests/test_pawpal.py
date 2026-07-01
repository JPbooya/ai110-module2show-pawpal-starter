from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task("Morning walk", "08:00", "daily")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task("Feeding", "07:30", "daily"))

    assert len(pet.get_tasks()) == 1


def test_organize_by_time_sorts_chronologically():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Evening walk", "18:00", "daily"))
    pet.add_task(Task("Morning walk", "08:00", "daily"))
    owner.add_pet(pet)

    schedule = Scheduler(owner).organize_by_time()

    assert [t.description for t in schedule] == ["Morning walk", "Evening walk"]


def test_filter_tasks_by_pet_and_status():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    whiskers = Pet("Whiskers", "cat")
    mochi.add_task(Task("Walk", "08:00", "daily"))
    feeding = Task("Feeding", "07:30", "daily")
    feeding.mark_complete()
    whiskers.add_task(feeding)
    owner.add_pet(mochi)
    owner.add_pet(whiskers)
    scheduler = Scheduler(owner)

    assert [t.description for t in scheduler.filter_tasks(pet_name="Mochi")] == ["Walk"]
    assert [t.description for t in scheduler.filter_tasks(status="completed")] == ["Feeding"]
    assert [t.description for t in scheduler.filter_tasks(status="pending")] == ["Walk"]


def test_weekly_task_is_only_due_on_its_day():
    task = Task("Grooming", "09:00", "weekly", day_of_week="Monday")

    assert task.is_due_on("Monday") is True
    assert task.is_due_on("Tuesday") is False


def test_completing_daily_task_creates_next_occurrence():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Feeding", "07:30", "daily"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    original = pet.get_tasks()[0]

    next_task = scheduler.complete_task(original)

    assert original.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.description == "Feeding"
    assert next_task.time == "07:30"
    assert next_task in pet.get_tasks()
    assert len(pet.get_tasks()) == 2


def test_completing_weekly_task_creates_next_occurrence_same_day():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Grooming", "09:00", "weekly", day_of_week="Monday"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    original = pet.get_tasks()[0]

    next_task = scheduler.complete_task(original)

    assert next_task is not None
    assert next_task.day_of_week == "Monday"
    assert next_task.completed is False


def test_completing_once_task_does_not_create_next_occurrence():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Vet visit", "10:00", "once"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    task = pet.get_tasks()[0]

    next_task = scheduler.complete_task(task)

    assert task.completed is True
    assert next_task is None
    assert len(pet.get_tasks()) == 1


def test_find_conflicts_detects_overlapping_times_for_same_pet():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", "08:00", "daily", duration_minutes=30))
    pet.add_task(Task("Vet visit", "08:15", "daily", duration_minutes=30))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    conflicts = scheduler.find_conflicts(day_of_week="Monday")

    assert len(conflicts) == 1
    descriptions = {conflicts[0][0].description, conflicts[0][1].description}
    assert descriptions == {"Walk", "Vet visit"}


def test_find_conflicts_detects_overlapping_times_across_different_pets():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    whiskers = Pet("Whiskers", "cat")
    mochi.add_task(Task("Walk", "08:00", "daily", duration_minutes=30))
    whiskers.add_task(Task("Feeding", "08:15", "daily", duration_minutes=30))
    owner.add_pet(mochi)
    owner.add_pet(whiskers)
    scheduler = Scheduler(owner)

    conflicts = scheduler.find_conflicts(day_of_week="Monday")

    assert len(conflicts) == 1
    descriptions = {conflicts[0][0].description, conflicts[0][1].description}
    assert descriptions == {"Walk", "Feeding"}


def test_find_owning_pet_returns_correct_pet():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    whiskers = Pet("Whiskers", "cat")
    mochi_task = Task("Walk", "08:00", "daily")
    mochi.add_task(mochi_task)
    owner.add_pet(mochi)
    owner.add_pet(whiskers)
    scheduler = Scheduler(owner)

    assert scheduler.find_owning_pet(mochi_task) is mochi


def test_check_for_conflicts_warns_on_shared_start_time():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    whiskers = Pet("Whiskers", "cat")
    mochi.add_task(Task("Walk", "08:00", "daily"))
    whiskers.add_task(Task("Feeding", "08:00", "daily"))
    owner.add_pet(mochi)
    owner.add_pet(whiskers)
    scheduler = Scheduler(owner)

    warning = scheduler.check_for_conflicts(day_of_week="Monday")

    assert "08:00" in warning
    assert "Mochi's Walk" in warning
    assert "Whiskers's Feeding" in warning


def test_check_for_conflicts_returns_empty_string_when_no_conflicts():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", "08:00", "daily"))
    pet.add_task(Task("Feeding", "09:00", "daily"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    assert scheduler.check_for_conflicts(day_of_week="Monday") == ""


def test_check_for_conflicts_does_not_raise_on_malformed_time():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", "not-a-time", "daily"))
    pet.add_task(Task("Feeding", "not-a-time", "daily"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    warning = scheduler.check_for_conflicts(day_of_week="Monday")

    assert "not-a-time" in warning


# --- Edge case tests ---


def test_organize_by_time_keeps_all_tasks_with_identical_start_times():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", "08:00", "daily"))
    pet.add_task(Task("Feeding", "08:00", "daily"))
    owner.add_pet(pet)

    schedule = Scheduler(owner).organize_by_time()

    descriptions = [t.description for t in schedule]
    assert "Walk" in descriptions
    assert "Feeding" in descriptions
    assert len(schedule) == 2


def test_organize_by_time_handles_midnight_and_late_night_tasks():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Late meds", "23:30", "daily"))
    pet.add_task(Task("Midnight snack", "00:00", "daily"))
    pet.add_task(Task("Noon feeding", "12:00", "daily"))
    owner.add_pet(pet)

    schedule = Scheduler(owner).organize_by_time()

    assert [t.description for t in schedule] == ["Midnight snack", "Noon feeding", "Late meds"]


def test_organize_by_time_excludes_weekly_tasks_not_due_today():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Monday grooming", "09:00", "weekly", day_of_week="Monday"))
    pet.add_task(Task("Daily walk", "08:00", "daily"))
    owner.add_pet(pet)

    schedule = Scheduler(owner).organize_by_time(day_of_week="Tuesday")

    descriptions = [t.description for t in schedule]
    assert "Monday grooming" not in descriptions
    assert "Daily walk" in descriptions


def test_next_occurrence_preserves_duration_minutes():
    task = Task("Long walk", "08:00", "daily", duration_minutes=60)

    next_task = task.next_occurrence()

    assert next_task is not None
    assert next_task.duration_minutes == 60


def test_completing_already_completed_task_adds_another_occurrence():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Feeding", "07:30", "daily"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    original = pet.get_tasks()[0]

    scheduler.complete_task(original)
    scheduler.complete_task(original)

    assert len(pet.get_tasks()) == 3


def test_chained_completion_creates_further_occurrence():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Feeding", "07:30", "daily"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    original = pet.get_tasks()[0]

    next_task = scheduler.complete_task(original)
    scheduler.complete_task(next_task)

    assert len(pet.get_tasks()) == 3
    assert pet.get_tasks()[2].completed is False


def test_filter_tasks_with_unknown_pet_name_returns_empty():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", "08:00", "daily"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    result = scheduler.filter_tasks(pet_name="Ghost")

    assert result == []


def test_filter_tasks_combined_pet_and_status():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    mochi.add_task(Task("Walk", "08:00", "daily"))
    feeding = Task("Feeding", "07:30", "daily")
    feeding.mark_complete()
    mochi.add_task(feeding)
    owner.add_pet(mochi)
    scheduler = Scheduler(owner)

    result = scheduler.filter_tasks(pet_name="Mochi", status="pending")

    assert len(result) == 1
    assert result[0].description == "Walk"


def test_find_conflicts_does_not_flag_back_to_back_tasks():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", "08:00", "daily", duration_minutes=30))
    pet.add_task(Task("Feeding", "08:30", "daily", duration_minutes=30))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    conflicts = scheduler.find_conflicts(day_of_week="Monday")

    assert conflicts == []


def test_find_conflicts_returns_all_pairs_for_three_overlapping_tasks():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", "08:00", "daily", duration_minutes=30))
    pet.add_task(Task("Feeding", "08:00", "daily", duration_minutes=30))
    pet.add_task(Task("Grooming", "08:00", "daily", duration_minutes=30))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    conflicts = scheduler.find_conflicts(day_of_week="Monday")

    assert len(conflicts) == 3
