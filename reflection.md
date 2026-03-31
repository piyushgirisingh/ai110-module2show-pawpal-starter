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
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

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
