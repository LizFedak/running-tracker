# Running Tracker

Run it:

```
python3 serve.py
```

Your browser opens to http://localhost:8000. Edit files, then refresh.

- **Weeks**: a table of every week with goal miles, completed miles and %.
- **Week pages**: click a week to see it. Use "Print this page" (or Cmd+P) to print it for the binder.

## Workflow (in the IDE with Claude)
1. Fill in `profile.md` once.
2. Each week, ask: **"plan next week"**
3. As you run, tell Claude: **"ran 4 today"**, or edit the Actual mi column yourself.
4. At the end of the week, ask: **"help me write this week's reflection"**

The planning rules are in `CLAUDE.md`.

## Deployed site (Vercel)
Vercel runs `python3 serve.py --build`, which writes static HTML to `public/` (see `vercel.json`). Every push to GitHub redeploys the site. `profile.md` is left out of the deployed site on purpose.
