from pawpal_system import Pet, Task


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
