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
