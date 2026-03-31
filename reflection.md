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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
