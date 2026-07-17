# Roadmap — InstaGraber

Rule: a step is **done** only after its check passes. Then: tick the box here, add a PROJECT_LOG.md entry, `git commit`, `git push`.

- [x] **Step 0 — Scaffold & repo**
  Project docs, .gitignore, .env template, config.json, requirements.txt; git init + first commit; private GitHub repo + push.
  *Check:* `git log` shows the commit; repo visible on GitHub. *(Push pending — needs `gh auth login` from the user.)*

- [ ] **Step 1 — Credentials & environment** *(needs user actions first — see README setup)*
  Telegram bot token in `.env`; dependencies installed; Instagram session created via `instaloader --login`.
  *Check:* test script sends a "hello" message to the owner's Telegram chat; instaloader session loads without asking for a password.

- [ ] **Step 2 — Story fetcher**
  `ig_watcher.py`: given the target username from `config.json`, list its currently-active story items (id, timestamp, photo/video, media URL).
  *Check:* run it manually against an account that currently has stories; items print correctly.

- [ ] **Step 3 — Notifier loop**
  Repeating job every `poll_interval_minutes`: fetch stories, diff against `state.json`, send a Telegram alert (with the media attached when possible) for each unseen item. First run for a new account baselines silently (no spam for old stories).
  *Check:* point it at an account with live stories and an empty state → exactly those notifications arrive once; second run sends nothing.

- [ ] **Step 4 — Runtime commands (change target account from Telegram)**
  `/watch <username>` — validate the account exists, update `config.json`, take effect without restart; `/status`, `/check` (force a poll now), `/help`. Bot ignores everyone except the owner chat id.
  *Check:* drive every command from the owner's Telegram; switch target to another account live and get its notifications.

- [ ] **Step 5 — Hardening**
  Detect expired/invalid Instagram session → warn the owner on Telegram instead of crashing; retry with backoff on rate limits; log to `logs/`; guard against unhandled exceptions.
  *Check:* rename the session file to simulate expiry → owner gets a warning message and the bot stays alive.

- [ ] **Step 6 — Run forever on Windows**
  Auto-start at logon via Task Scheduler; final README polish.
  *Check:* log off/on (or reboot) → bot is running without manually starting it.
