# Running Tracker — Planning Instructions

A personal, local-only running log. Each week is one markdown file in `weeks/`, viewed and printed via `python3 serve.py`. There are no users, logins or databases, and nothing beyond the Python standard library. Keep it that way.

## Tone
Just a plan maker. Write plans and reasoning tersely, with facts and numbers. Don't add coaching advice, cautions or commentary about past decisions unless asked.

## Files
- `profile.md`: the runner's big goal, starting baseline, injury history and preferences. **Read this first.**
- `weeks/YYYY-MM-DD.md`: one file per week, named for the **Monday** that starts the week.
- `weeks/_template.md`: copy this structure for new weeks. Files starting with `_` are ignored by the viewer.
- `progress.md`: the running progress log, amended weekly (see below).
- `serve.py`: the viewer. Mileage comes from the frontmatter, or else from summing the table columns whose headers start with "Planned" and "Actual".

## When asked to "plan next week" (or a specific week)
1. Read `profile.md` and the most recent 3–4 week files, especially the **Actual mi** column and the **Reflection** section.
2. Read `progress.md`.
3. If anything important is unknown, ask briefly before writing: this week's schedule constraints, how the body feels, any pain. Don't invent facts about how the runner feels.
4. Create `weeks/<monday-date>.md` from the template, then fill in:
   - **Baseline**: facts only. Last week's actual vs. planned miles and %, 4-week average, longest recent run, how it felt (from Reflection/notes), and constraints for this week.
   - **Goal**: the ideal week if everything goes well: the next step toward the big goal in `profile.md`.
   - **Realistic plan**: the day-by-day table the runner commits to. This is what counts as the week's goal mileage, so it should usually be at or below the Goal.
   - **Reasoning**: 3–6 bullets that cite specific numbers ("last week 14/16 mi, 88%, so a modest bump to 17").
   - Leave **Reflection** as the placeholder, and leave **Actual mi** blank.
   - Set `focus:` to a 1–3 word label (Base, Build, Cutback, Peak, Taper, Race, Recovery).
5. Amend `progress.md` (see below).
6. Keep each week short enough to print on **one page**.
7. Use heart-rate zones (Z1–Z5, defined in `profile.md`) for intensity, not paces. Long runs and hard sessions go on weekdays. **Sat/Sun may only be CrossFit, easy runs or rest.** Yoga and hikes go on weekdays. Schedule 2–3 CrossFit days and avoid stacking them with runs when possible, and include yoga and hike days in the table with 0 planned mi.

## Weekly rotation
Rotate the quality type every 4 weeks, starting with `weeks/2026-11-09.md` as week 1. See the rotation table in `profile.md`: Easy → Strides → Tempo → Hills → repeat. Work out a week's rotation slot by counting weeks since 2026-11-09, mod 4. Put the type in `focus:` (e.g. `Base 2 · Strides`). The Easy week doubles as the cutback week.

## Planning guardrails
- **Weekly miles = previous week's planned miles +10%**, rounded to the nearest 0.5. Follow the Projection table in `profile.md`.
- **Every 4th week is a cutback** (~25% below the week before; weeks 5, 9, 13, 17, the Easy rotation weeks). The week after a cutback builds 10% from the last full week.
- **The long run never goes above 16 mi.** Keep it at roughly 35–40% of weekly miles.
- No race is scheduled. If one is added, add a taper before it.
- Mostly easy running (~80%). No back-to-back hard days. Add at most 1 quality session per week until the base is solid.
- If pain or injury comes up, put recovery first: reduce or rest, and suggest seeing a professional if it persists. Don't plan through pain.

## Progress doc (`progress.md`)
Amend it every week. Do this when planning the next week, or whenever asked:
- Fill in last week's row in the log table: planned, actual, %, long run planned / actual.
- Add the next week's row with planned miles and long run (leave actuals blank).
- Update the "To date" numbers at the top.
- Add a short entry under "Week by week" for the week that just ended: 1–3 lines taken from the week's Notes and Reflection.
Never rewrite past entries. Only append to them or fill in blanks.

## When logging runs
- "Ran 4 today" / "did 6 on Saturday": fill in the **Actual mi** cell (and Notes if useful) for that day in the current week's file. Work out the dates from today's date and the Monday file name.
- Skipped run: put `0` in Actual and a short note.
- Don't change Planned mi after the fact. If the plan changed mid-week, mention it in Notes.
- At the end of the week, help write the Reflection if asked.
