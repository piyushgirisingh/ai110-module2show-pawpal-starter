from pawpal_system import Owner, Pet, Scheduler, Task

# --- Pets ---
mochi = Pet(name="Mochi", species="dog", age=4, special_needs=["joint supplement"])
luna = Pet(name="Luna", species="cat", age=7, special_needs=["hyperthyroid medication"])

# --- Owner ---
jordan = Owner(name="Jordan", available_minutes=90, pets=[mochi, luna])

# --- Scheduler (one per pet) ---
mochi_scheduler = Scheduler(pet=mochi, owner=jordan)
luna_scheduler = Scheduler(pet=luna, owner=jordan)

# --- Tasks for Mochi ---
mochi_scheduler.add_task(Task(
    title="Morning walk",
    task_type="walk",
    duration_minutes=30,
    priority="high",
    pet_name="Mochi",
    latest_start_time="08:00",
))
mochi_scheduler.add_task(Task(
    title="Breakfast feeding",
    task_type="feeding",
    duration_minutes=10,
    priority="high",
    pet_name="Mochi",
))
mochi_scheduler.add_task(Task(
    title="Joint supplement",
    task_type="medication",
    duration_minutes=5,
    priority="medium",
    pet_name="Mochi",
))
mochi_scheduler.add_task(Task(
    title="Enrichment puzzle toy",
    task_type="enrichment",
    duration_minutes=20,
    priority="low",
    pet_name="Mochi",
))

# --- Tasks for Luna ---
luna_scheduler.add_task(Task(
    title="Thyroid medication",
    task_type="medication",
    duration_minutes=5,
    priority="high",
    pet_name="Luna",
    latest_start_time="07:30",
))
luna_scheduler.add_task(Task(
    title="Breakfast feeding",
    task_type="feeding",
    duration_minutes=10,
    priority="high",
    pet_name="Luna",
))
luna_scheduler.add_task(Task(
    title="Grooming brush",
    task_type="grooming",
    duration_minutes=15,
    priority="low",
    pet_name="Luna",
))

# --- Generate and print plans ---
separator = "-" * 40

print("=" * 40)
print("       TODAY'S SCHEDULE — PawPal+")
print("=" * 40)
print(f"Owner : {jordan.name}")
print(f"Budget: {jordan.get_time_budget()} minutes")
print()

for scheduler in [mochi_scheduler, luna_scheduler]:
    plan = scheduler.generate_plan()
    print(separator)
    print(plan.display())
    summary = plan.get_summary()
    print(f"  Scheduled: {summary['scheduled_count']} tasks | "
          f"Dropped: {summary['dropped_count']} | "
          f"Time used: {summary['total_duration_minutes']} min")

print(separator)
