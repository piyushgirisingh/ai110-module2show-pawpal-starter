from pawpal_system import Pet, Task


def make_task(title="Morning walk", priority="medium"):
    return Task(
        title=title,
        task_type="walk",
        duration_minutes=20,
        priority=priority,
    )


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_to_pet_increases_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert pet.task_count() == 0
    pet.add_task(make_task("Morning walk"))
    assert pet.task_count() == 1
    pet.add_task(make_task("Feeding"))
    assert pet.task_count() == 2
