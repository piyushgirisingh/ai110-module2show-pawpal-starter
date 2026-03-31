from pawpal_system import Owner, Pet, Scheduler, Task

MORNING_WALK = "Morning walk"
EVENING_WALK = "Evening walk"

# --- Pets ---
mochi = Pet(name="Mochi", species="dog", age=4, special_needs=["joint supplement"])
luna = Pet(name="Luna", species="cat", age=7, special_needs=["hyperthyroid medication"])

# --- Owner ---
jordan = Owner(name="Jordan", available_minutes=90, pets=[mochi, luna])

# --- Single shared scheduler so sort/filter span both pets ---
scheduler = Scheduler(pet=mochi, owner=jordan)

# Tasks added intentionally OUT OF ORDER (latest deadline first, then no deadline)
scheduler.add_task(Task(
    title="Enrichment puzzle toy",
    task_type="enrichment",
    duration_minutes=20,
    priority="low",
    pet_name="Mochi",
    # no deadline
))
scheduler.add_task(Task(
    title=EVENING_WALK,
    task_type="walk",
    duration_minutes=30,
    priority="medium",
    pet_name="Mochi",
    latest_start_time="17:00",
))
scheduler.add_task(Task(
    title="Thyroid medication",
    task_type="medication",
    duration_minutes=5,
    priority="high",
    pet_name="Luna",
    latest_start_time="07:30",
    recurrence="daily",
))
scheduler.add_task(Task(
    title="Joint supplement",
    task_type="medication",
    duration_minutes=5,
    priority="medium",
    pet_name="Mochi",
    latest_start_time="09:00",
))
scheduler.add_task(Task(
    title="Grooming brush",
    task_type="grooming",
    duration_minutes=15,
    priority="low",
    pet_name="Luna",
    recurrence="weekly",
))
scheduler.add_task(Task(
    title=MORNING_WALK,
    task_type="walk",
    duration_minutes=30,
    priority="high",
    pet_name="Mochi",
    latest_start_time="08:00",
    recurrence="daily",
))
scheduler.add_task(Task(
    title="Breakfast feeding",
    task_type="feeding",
    duration_minutes=10,
    priority="high",
    pet_name="Mochi",
    latest_start_time="08:30",
))
scheduler.add_task(Task(
    title="Luna dinner",
    task_type="feeding",
    duration_minutes=10,
    priority="high",
    pet_name="Luna",
    latest_start_time="18:00",
))

SEP = "-" * 48
NO_DEADLINE = "none "

# -----------------------------------------------------------------------
# 1. Raw insertion order (before any sort)
# -----------------------------------------------------------------------
print("=" * 48)
print("  TASKS AS ADDED (insertion order)")
print("=" * 48)
for t in scheduler.tasks:
    deadline = t.latest_start_time.strftime("%H:%M") if t.latest_start_time else NO_DEADLINE
    done = "✓" if t.completed else " "
    print(f"  [{done}] {deadline}  [{t.priority:>6}]  {t.pet_name:<6}  {t.title}")

# -----------------------------------------------------------------------
# 2. sort_by_time() — earliest deadline first, no-deadline tasks last
# -----------------------------------------------------------------------
print()
print(SEP)
print("  SORTED BY TIME (sort_by_time)")
print(SEP)
for t in scheduler.sort_by_time():
    deadline = t.latest_start_time.strftime("%H:%M") if t.latest_start_time else NO_DEADLINE
    done = "✓" if t.completed else " "
    print(f"  [{done}] {deadline}  [{t.priority:>6}]  {t.pet_name:<6}  {t.title}")

# -----------------------------------------------------------------------
# 3. filter_tasks — by pet name
# -----------------------------------------------------------------------
print()
print(SEP)
print("  FILTER: pet_name='Mochi'")
print(SEP)
for t in scheduler.filter_tasks(pet_name="Mochi"):
    deadline = t.latest_start_time.strftime("%H:%M") if t.latest_start_time else NO_DEADLINE
    done = "✓" if t.completed else " "
    print(f"  [{done}] {deadline}  [{t.priority:>6}]  {t.title}")

print()
print(SEP)
print("  FILTER: pet_name='Luna'")
print(SEP)
for t in scheduler.filter_tasks(pet_name="Luna"):
    deadline = t.latest_start_time.strftime("%H:%M") if t.latest_start_time else NO_DEADLINE
    done = "✓" if t.completed else " "
    print(f"  [{done}] {deadline}  [{t.priority:>6}]  {t.title}")

# -----------------------------------------------------------------------
# 4. filter_tasks — by completion status
# -----------------------------------------------------------------------
print()
print(SEP)
print("  FILTER: completed=True")
print(SEP)
for t in scheduler.filter_tasks(completed=True):
    print(f"  [✓] {t.pet_name:<6}  {t.title}")

print()
print(SEP)
print("  FILTER: completed=False  (pending)")
print(SEP)
for t in scheduler.filter_tasks(completed=False):
    print(f"  [ ] {t.pet_name:<6}  {t.title}")

# -----------------------------------------------------------------------
# 5. filter_tasks — combined (pet + status)
# -----------------------------------------------------------------------
print()
print(SEP)
print("  FILTER: pet_name='Mochi' + completed=False")
print(SEP)
for t in scheduler.filter_tasks(pet_name="Mochi", completed=False):
    deadline = t.latest_start_time.strftime("%H:%M") if t.latest_start_time else NO_DEADLINE
    print(f"  [ ] {deadline}  [{t.priority:>6}]  {t.title}")

print()
print(SEP)

# -----------------------------------------------------------------------
# 6. complete_task() — recurring tasks spawn the next occurrence
# -----------------------------------------------------------------------
def show_tasks(label: str) -> None:
    print()
    print(SEP)
    print(f"  {label}")
    print(SEP)
    for t in scheduler.tasks:
        deadline = t.latest_start_time.strftime("%H:%M") if t.latest_start_time else NO_DEADLINE
        done = "✓" if t.completed else " "
        recur = f"[{t.recurrence}]" if t.is_recurring() else "       "
        print(f"  [{done}] {deadline}  {recur}  {t.pet_name:<6}  {t.title}  (due: {t.due_date_str()})")

show_tasks("BEFORE completing any recurring tasks")

next_task = scheduler.complete_task(MORNING_WALK)
print(f"\n  complete_task('Morning walk') → spawned: '{next_task.title}' (recurs {next_task.recurrence}, due: {next_task.due_date_str()})")

next_task = scheduler.complete_task("Thyroid medication")
print(f"  complete_task('Thyroid medication') → spawned: '{next_task.title}' (recurs {next_task.recurrence}, due: {next_task.due_date_str()})")

next_task = scheduler.complete_task("Grooming brush")
print(f"  complete_task('Grooming brush') → spawned: '{next_task.title}' (recurs {next_task.recurrence}, due: {next_task.due_date_str()})")

result = scheduler.complete_task(EVENING_WALK)
print(f"  complete_task('Evening walk') → spawned: {result}  (not recurring — no new task)")

show_tasks("AFTER completing recurring tasks (new occurrences appended)")

print()
print(SEP)
print("  FILTER: completed=True  (what was just finished)")
print(SEP)
for t in scheduler.filter_tasks(completed=True):
    recur = f"[{t.recurrence}]" if t.is_recurring() else "       "
    print(f"  [✓] {recur}  {t.pet_name:<6}  {t.title}")

print()
print(SEP)
print("  FILTER: completed=False  (pending — includes new occurrences)")
print(SEP)
for t in scheduler.filter_tasks(completed=False):
    recur = f"[{t.recurrence}]" if t.is_recurring() else "       "
    print(f"  [ ] {recur}  {t.pet_name:<6}  {t.title}")

print()
print(SEP)

# -----------------------------------------------------------------------
# 7. quick_conflict_check() — same-time tasks trigger a warning
# -----------------------------------------------------------------------
print()
print(SEP)
print("  CONFLICT CHECK — no overlap (clear schedule)")
print(SEP)
clear_scheduler = Scheduler(pet=mochi, owner=jordan, day_start="06:00")
clear_scheduler.add_task(Task(MORNING_WALK,     "walk",    30, "high",   pet_name="Mochi", latest_start_time="08:00"))
clear_scheduler.add_task(Task("Breakfast feeding","feeding", 10, "high",   pet_name="Mochi", latest_start_time="09:00"))
clear_scheduler.add_task(Task(EVENING_WALK,     "walk",    30, "medium", pet_name="Mochi", latest_start_time="17:00"))
result = clear_scheduler.quick_conflict_check()
print(f"  quick_conflict_check() → {result or 'None (no conflicts)'}")

print()
print(SEP)
print("  CONFLICT CHECK — Mochi & Luna tasks overlap at 08:15")
print(SEP)
conflict_scheduler = Scheduler(pet=mochi, owner=jordan, day_start="06:00")
conflict_scheduler.add_task(Task(MORNING_WALK, "walk",  30, "high",   pet_name="Mochi", latest_start_time="08:00"))
conflict_scheduler.add_task(Task("Luna grooming","groom", 20, "medium", pet_name="Luna",  latest_start_time="08:15"))
conflict_scheduler.add_task(Task("Thyroid meds", "meds",   5, "high",   pet_name="Luna",  latest_start_time="08:00"))
result = conflict_scheduler.quick_conflict_check()
print(f"  quick_conflict_check() → {result}")

print()
print(SEP)
