# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Essentially a user should be allowed to be logged in for the app, so it has all the user information like pets, schedule etc..The user should also be allowed to add a pet and their information. User's are also allowed to add schedule and customize them.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

No major changes at all from the inital design, only a couple of tweaks for users values that I told the Ai to modify so that it make sense.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler has two conflict-detection methods that trade accuracy for robustness. `find_conflicts()` is duration-aware: it parses each task's `time` into minutes and checks whether the actual time windows overlap, so it catches partial overlaps (e.g. a 30-minute walk at 08:00 colliding with a vet visit starting at 08:15). The cost is that parsing can throw an exception if a task has a malformed time string (like "noon" instead of "08:00"), which the app's free-text time field made easy to enter by accident.

`check_for_conflicts()` instead groups tasks by their exact `time` string with no parsing at all, so it can never crash on bad input — but it only flags tasks that start at the literal same time, missing partial overlaps like 08:00–08:30 and 08:15–08:45.

I used the lightweight version in the interactive app, since a typo in a time field is a near-certain occurrence for a real user, and missing a partial-overlap warning is a much smaller cost than crashing the whole scheduling page. The duration-aware version stays available for cases where input is already trusted/validated.

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
