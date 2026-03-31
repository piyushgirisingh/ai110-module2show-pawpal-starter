# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

The initial UML design should have the option to add a pet, schedule a care task and see today's prioritized plan.

 The user registers their pet by entering basic information such as the pet's name, species, age, and any special needs or medical conditions. This creates a Pet profile in the system that all tasks and schedules are attached to. Without this step, nothing else can be personalized to the animal's specific care requirements.

 The user adds a task (such as a walk, feeding, medication dose, grooming, or vet appointment) for their pet by specifying the task type, estimated duration, priority level, and any time constraints (e.g., "must happen before noon"). This is the primary way the owner communicates what needs to get done, and it feeds the scheduling algorithm with the raw data it needs to build a daily plan.

 The user requests a generated daily schedule that the system builds by ordering pending tasks according to priority, duration, and any constraints. The plan is displayed clearly so the owner knows exactly what to do and when, along with a brief explanation of why the tasks are ordered that way 

- What classes did you include, and what responsibilities did you assign to each?

I included the pet, the owner of the pet, the task, the scheduler and the daily plan.

Pet stores the animal's profile: name, species, age, and any special needs or medical flags. Every task and schedule is anchored to a Pet instance, so it acts as the central data object the rest of the system revolves around.

Owner stores the human's information: name and the total number of minutes available in the day. The scheduler reads the owner's available time as its primary capacity constraint when deciding how many tasks can fit.

Task represents a single care item (walk, feeding, medication, grooming, appointment, etc.). Attributes include title, task type, duration in minutes, priority level (low / medium / high), and an optional latest-start-time constraint. This is the unit of work the scheduler sorts and selects from.

Scheduler contains the algorithm that receives a list of Task objects and an Owner's available time, then produces an ordered daily plan. Its core responsibility is sorting tasks by priority (high first), fitting them within the time budget, and generating a short reason string for each selected task explaining why it was placed in that position.

Daily Plan is a lightweight container that holds the final ordered list of scheduled tasks along with any tasks that were dropped (and why). It is what gets passed to the UI for display, keeping the output separate from the algorithm that produced it.

**b. Design changes**

- Did your design change during implementation?

Yes

- If yes, describe at least one change and why you made it.

The most significant change was to `Task`: the initial design had no link back to which pet the task belonged to, and `latest_start_time` was stored as a plain string. Both were problems waiting to happen. A `pet_name` attribute was added so tasks can be associated with a specific animal, which matters as soon as the app supports more than one pet. The `latest_start_time` field was changed to parse the input string into a `datetime.time` object at construction time, so the scheduler can actually compare it against a clock value rather than hitting a type error at runtime.


## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers three constraints: **time** (the owner's daily minute budget), **deadlines** (a task's `latest_start_time`), and **priority** (high / medium / low). Time is the hard outer limit — no task can be added once the budget is exhausted. Deadlines come second: a task that must happen before noon needs to be placed before tasks with no time constraint, regardless of priority. Priority is the final tiebreaker when two tasks share the same deadline or neither has one.

I decided this ordering by thinking about real pet care: missing a medication window has a concrete consequence (the animal doesn't get its dose), while doing a lower-priority grooming session slightly earlier instead of slightly later has almost no consequence. Time-sensitivity and urgency therefore outrank a subjective importance label. The owner's time budget is inviolable because the scheduler must produce a plan the owner can actually execute — an over-scheduled plan is worthless.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

**Greedy sequential scheduling instead of optimal packing**

The scheduler uses a greedy algorithm: it sorts tasks by earliest deadline then descending priority, then walks the list once and schedules each task if it fits within the remaining time budget. A task that is too long to fit is dropped immediately — the scheduler never backtracks to check whether a shorter lower-priority task could fill the remaining minutes.

The consequence is that the schedule is not always optimal. For example, if the owner has 15 minutes left and one 20-minute task followed by one 10-minute task, the greedy approach drops both (the 20-minute task doesn't fit, and by the time the 10-minute task is reached the slot is still open but it was sorted after the larger task). A knapsack-style algorithm would catch the 10-minute task and fill the gap.

This tradeoff is reasonable for a pet care app for two reasons. First, pet care tasks are not arbitrary items to pack — they have real-world sequencing constraints (medication before breakfast, walk before the heat of the day) that a pure knapsack solver would ignore. The greedy approach respects the priority and deadline ordering that the owner explicitly set. Second, the number of daily tasks for one or two pets is small (typically under 15), so the difference between greedy and optimal output is unlikely to matter in practice. The simplicity of a single-pass O(n log n) sort plus O(n) scan is easier to reason about, test, and explain to a non-technical user than a combinatorial solver.


## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

AI tools were used across every phase of the project. During **design**, I described the app concept in plain English and asked Copilot Chat to suggest class responsibilities and attribute types — this produced the first draft of the UML diagram. During **implementation**, Copilot's inline completions filled in boilerplate (dataclass field declarations, `__repr__` methods, Streamlit column layouts) so I could focus on the logic. During **debugging**, I pasted failing test output into the chat and asked "why does this assertion fail?" — the explanation usually pointed me to the exact line. During **refactoring**, I asked "how can I separate conflict detection from plan generation?" which led to splitting `detect_conflicts()` into `_deadline_conflicts()` and `_overlap_conflicts()` private helpers.

The most productive prompts were specific and constrained: "Given this class signature, write a method that sorts tasks by deadline then priority, returning the sorted list" worked far better than "make the scheduler smarter." Asking Copilot to explain *why* it chose an approach (not just what) helped me decide whether to accept the suggestion.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When I asked Copilot to implement `generate_plan()`, its first suggestion stored scheduled tasks inside `DailyPlan` as a flat list of `Task` objects. I rejected this because the UI needed both the task *and* a human-readable reason string for why it was scheduled or dropped — a flat list would have required a second lookup pass or side-channel dictionary. I modified the design so `scheduled` and `dropped` are each a list of `(Task, reason: str)` tuples, matching exactly what `app.py` unpacks. I verified the change by tracing through the display loop in `app.py` and confirming that `for task, reason in plan.scheduled` would work cleanly without any extra data structures.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The test suite covers four areas. **Sorting** tests verify that `sort_by_time()` returns tasks in earliest-deadline-first order, that priority breaks ties correctly (high before medium before low at the same deadline), that tasks without a deadline always appear last, and that an empty task list returns an empty list. **Recurrence** tests check that `complete_task()` correctly calculates the next daily and weekly due dates, that a non-recurring task returns `None` from `complete_task()`, that the new occurrence inherits the original deadline, and that completing an unknown title raises no error. **Conflict detection** tests confirm that two tasks with the same `latest_start_time` are flagged as a shared-deadline conflict, that two tasks whose time windows overlap are flagged as an overlap conflict, that a clean schedule with no overlap produces an empty conflict list, and that `quick_conflict_check()` returns a non-empty string when at least one conflict exists. **Task management** tests verify that `mark_complete()` sets `task.completed = True` and that `add_task()` increments the pet's task count.

These tests matter because the scheduler's correctness depends entirely on sort order and conflict logic — if sorting is wrong, every generated plan is wrong. Testing the boundary cases (no deadline, same deadline, zero tasks) catches the branches that casual manual testing misses.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am confident the scheduler handles the standard cases correctly: the 15 sorting + recurrence + conflict tests all pass, and I manually verified the Streamlit UI against known inputs. I am less confident about boundary conditions that the current suite does not cover. If I had more time I would test: a task whose `duration_minutes` exactly equals the remaining budget (should schedule, not drop); two tasks that together fit but individually arrive in an order that causes the first to be dropped (greedy miss); a `latest_start_time` that has already passed when the scheduler runs (should it be flagged immediately?); and `filter_tasks()` with `completed=None` to verify the "all" path. I would also add a test that runs `generate_plan()` end-to-end and checks that `summary["scheduled_count"] + summary["dropped_count"]` equals the total number of tasks.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The part I am most satisfied with is the conflict detection system. It was the most algorithmically interesting piece and the hardest to get right. Splitting it into three distinct checks — deadline miss (does the sequential schedule push a task past its deadline?), shared deadline (do two tasks claim the same latest-start time?), and time-window overlap (do two tasks' `[start, end)` intervals intersect?) — made each check small enough to unit test in isolation, while the public `detect_conflicts()` method composes them into a single list the UI can display. The live `quick_conflict_check()` that re-runs on every render without a button click was also a good UX decision: owners see warnings appear the moment a problematic task is added, rather than discovering conflicts only after generating the full plan.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would redesign the time budget model. Currently `available_minutes` is a single integer on `Owner`, and the scheduler treats the whole day as one continuous block. A more realistic model would let the owner specify availability windows (e.g., 07:00–09:00 and 17:00–19:00), and the scheduler would assign tasks to slots rather than just tracking elapsed minutes. This would make conflict detection more meaningful — a task that fits in the time budget might still be unschedulable because it lands in a gap between availability windows. I would also add persistent storage (a simple JSON file) so tasks survive a page reload, since losing the task list every time the Streamlit session restarts is the biggest practical friction point.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important thing I learned is that the value of a UML diagram is not the diagram itself — it is the questions you are forced to answer before writing a single line of code. When I mapped out the class relationships, I had to decide: who owns the task list, the Pet or the Scheduler? What type does `latest_start_time` need to be to support comparison operations? Those decisions, made early on paper, meant the implementation had almost no structural rework. AI tools are fast at generating code but they cannot make those architectural decisions for you — they will generate plausible-looking code that encodes whatever ambiguity you left in your prompt. The architect's job is to resolve the ambiguity before asking the AI to build.

---

## 6. AI Strategy — VS Code Copilot

**a. Most effective Copilot features**

The two features that saved the most time were **inline completions** and **Copilot Chat with file context**.

Inline completions were most effective during the implementation of `Scheduler`: once I typed `def _sort_tasks(self)` and a docstring describing the sort key, Copilot predicted the entire body — `sorted(self.tasks, key=lambda t: (t.latest_start_time or datetime.time(23,59), -t.get_priority_value()))` — which matched my design intent almost exactly. The same happened for boilerplate-heavy parts of `app.py`: column layouts, metric widgets, and `st.dataframe` column configs were completed after typing the first widget in a block.

Copilot Chat with `@workspace` context was the most effective feature for debugging. When `detect_conflicts()` was returning duplicate warnings, I attached the relevant file and asked "why might this method produce duplicate entries?" Copilot identified that `_overlap_conflicts()` was checking pairs `(i, j)` and `(j, i)` separately, and suggested switching to `itertools.combinations()` — a fix I could evaluate and apply in under a minute.

**b. One AI suggestion I rejected or modified**

When I asked Copilot Chat to suggest how to display the task list in the UI, it recommended a plain `st.table()` call rendering a list of dictionaries. I rejected this because `st.table()` is static — it cannot be resized and has no column width control. I modified the suggestion to use `st.dataframe()` with explicit `column_config` entries, which gave me control over column widths and rendered the priority field with emoji color badges. The Copilot suggestion was functionally correct but would have produced a cramped, unreadable table on a real screen. Evaluating it required me to mentally picture the rendered output, which is something the AI cannot do — it only sees the code.

**c. How separate chat sessions helped**

I used a separate Copilot Chat session for each project phase: one for UML design, one for implementing `pawpal_system.py`, one for building `app.py`, and one for writing tests. Keeping sessions separate meant each chat had a focused, coherent context — when I asked about scheduling logic in the second session, Copilot's suggestions were grounded in the class design I had finalized in the first session, not polluted by earlier half-finished ideas. It also made it easier to go back and revisit decisions: I could scroll through the design session to see why I made a particular choice, rather than hunting through a single long thread where design, implementation, and debugging questions were interleaved. In practice this mirrors how a professional team works — architecture review, implementation, and QA are separate conversations with separate audiences.

**d. Being the "lead architect" with AI**

Working with Copilot on this project made one thing clear: the AI is an extremely fast and capable junior developer who will execute whatever you describe, but it has no stake in whether the overall system is coherent. It will happily suggest storing data in two places, add a helper method that duplicates existing logic, or choose a data structure that works locally but causes a type error at the boundary between two modules — because it is responding to the immediate prompt, not reasoning about the whole system.

The lead architect's job is not to know every syntax detail (the AI handles that) — it is to hold the single coherent mental model of the system, make the decisions that require trade-off reasoning across multiple components, and review every AI suggestion against that model before accepting it. Concretely, that meant: deciding before coding that `DailyPlan.scheduled` would be `list[tuple[Task, str]]` rather than `list[Task]`; deciding that conflict detection and plan generation would be separate methods even though combining them would have been shorter; and deciding that `latest_start_time` would be a `datetime.time` object at the class boundary rather than a string. None of those decisions came from Copilot — they came from thinking about the whole system. The AI made executing those decisions fast. That is the right division of labor.
