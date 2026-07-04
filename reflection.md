# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

- My initial UML design for PawPal+ includes five main classes: Owner, Pet, CareTask, CarePlan, and PlanGenerator.

The Owner class represents the pet owner. It stores the owner’s name, available time, and preferences.

The Pet class stores basic information about the pet, such as name, species, and age.

The CareTask class represents one care activity, such as feeding, walking, medication, grooming, or enrichment. It stores the task title, category, priority, duration, preferred time, and completion status.

The CarePlan class represents the daily plan. It stores the date, total minutes, scheduled tasks, and an explanation of why the tasks were chosen.

The PlanGenerator class handles the planning logic. It sorts tasks by priority, checks which tasks fit into the owner’s available time, and builds the final care plan.

Main.py Sample output - 

=============================================
Today's Schedule for Maya
(Time available: 60 minutes)
=============================================

Pets:
  - Luna (cat, age 2) - 2 task(s)
  - Buddy (dog, age 4) - 3 task(s)

Planned tasks:
  1. Feed breakfast at 07:30 (daily, 10 min, priority 5) - not done
  2. Morning walk at 08:00 (daily, 30 min, priority 5) - not done
  3. Clean litter box at 12:00 (daily, 15 min, priority 3) - not done

Total time planned: 55 of 60 minutes
=============================================

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, my design changed during implementation. I simplified the design from five classes to four main classes: Task, Pet, Owner, and Scheduler.

I changed CareTask to Task to make the class name shorter and simpler. I also combined the CarePlan and PlanGenerator idea into the Scheduler class. The Scheduler now acts as the brain of the system because it collects tasks from the owner’s pets, sorts them by priority, and creates the daily plan.

This made the code easier to understand and matched the implementation in pawpal_system.py.

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
