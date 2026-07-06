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


My scheduler considers several constraints, including the owner's available time, task priority, completion status, task due date, and scheduled time. It also supports recurring tasks and checks for basic scheduling conflicts when tasks have the same due date and time.

I decided that available time and task priority were the most important because they help ensure the most important pet care tasks are completed first within the owner's time limit. Completion status prevents finished tasks from being scheduled again, while due dates and times help organize the daily schedule.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

## 2b. Tradeoffs

One tradeoff my scheduler makes is that it only checks for tasks with the exact same due date and time when detecting conflicts. It does not detect overlapping task durations or automatically rearrange the schedule. I chose this approach because it keeps the algorithm simple, easy to understand, and efficient while still identifying the most common scheduling conflicts for a pet owner.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI throughout the project to help brainstorm the initial UML design, implement the Python classes, write unit tests, improve the scheduling algorithms, and debug issues. I also used AI to help update my README and reflection files.

The most helpful prompts were specific questions such as "How should the Scheduler retrieve all tasks from the Owner's pets?", "How can I sort Task objects by time using Python?", and "What edge cases should I test for a pet scheduler with recurring tasks?". Using clear, focused prompts produced better suggestions.


**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One AI suggestion I did not fully accept was replacing my explicit conflict-detection loop with a more compact Python list comprehension. Although the AI version was shorter, I kept my original loop because it was easier to read, debug, and modify. I verified that my version produced the correct results by running my pytest test suite and confirming that all 22 tests passed.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested task completion, adding tasks to pets, sorting tasks by priority and time, generating daily schedules, filtering tasks, recurring task generation, and conflict detection. I also tested edge cases such as owners with no pets, pets with no tasks, and tasks with duplicate times.

These tests were important because they verified that the scheduler behaved correctly under both normal and unusual situations while helping prevent future changes from introducing bugs.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am confident that my scheduler works correctly because all 22 automated pytest tests passed successfully. The tests cover the main scheduling features as well as several important edge cases.

If I had more time, I would add tests for overlapping task durations, multiple recurring tasks on the same day, invalid time formats, and larger schedules with many pets and tasks.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The part I am most satisfied with is building the Scheduler class. It combines sorting, filtering, recurring tasks, and conflict detection into one organized component while keeping the code easy to understand.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

If I continued this project, I would improve the scheduling algorithm to detect overlapping task durations instead of only exact time matches. I would also make the Streamlit interface more interactive by allowing users to edit and delete pets and tasks.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

One important thing I learned is that AI is most effective when given clear, specific instructions. I also learned that I am responsible for making the final design decisions. AI can generate ideas and code quickly, but I need to review, test, and verify every suggestion to ensure it fits my system design and project requirements.
