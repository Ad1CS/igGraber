# Roadmap — InstaGraber

Rule: a step is **done** only after its check passes. Then: tick the box here, add a PROJECT_LOG.md entry, `git commit`, `git push`.

- [x] **Step 0 — Scaffold & repo**
  Project docs, .gitignore, .env template, config.json, requirements.txt; git init + first commit; GitHub repo + push.
  *Check:* `git log` shows the commit; pushed to https://github.com/Ad1CS/igGraber — done.

- [x] **Step 1 — Credentials & environment**
  Telegram bot token in `.env`; dependencies installed; Instagram session created via cookie import (`gleamflux`).
  *Check:* test message delivered to the owner's Telegram chat — done; `load_session_from_file` loads the session and successfully queries `magshimim_confessions` (1,461 followers) — done.

- [x] **Step 2 — Story fetcher**
  `ig_watcher.py`: given the target username from `config.json`, list its currently-active story items (id, timestamp, photo/video, media URL).
  *Check:* ran manually against `magshimim_confessions` (0 active, correct — no current story) and `instagram` (1 active item, fields parsed correctly) — done.

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
