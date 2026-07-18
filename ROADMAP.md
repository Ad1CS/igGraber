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

- [x] **Step 3 — Notifier loop**
  Repeating job every `poll_interval_minutes`: fetch stories, diff against `state.json`, send a Telegram alert (with the media attached when possible) for each unseen item. First run for a new target baselines silently (no spam for old stories).
  *Check:* tested with 4 controlled runs against `instagram` (has a live story) then the real target — baseline silent, repeat silent, simulated-new-story sent exactly 1 notification (confirmed delivered, message_id=3), revert-to-real-target baselined silently at 0 — all passed.
  *Update (Session 3):* now day/night aware — `poll_interval_minutes` (day, 06:00-24:00) and `night_poll_interval_minutes` (00:00-06:00) via two cron-triggered jobs, plus an immediate check 5s after startup. Configured 15 min day / 30 min night. Verified the cron trigger config directly (`cron[hour='6-23', minute='*/15']` and `cron[hour='0-5', minute='*/30']`) without touching Instagram.

- [x] **Step 4 — Runtime commands (change target account from Telegram)**
  `/watch <username or instagram.com profile URL>` — validate the account exists, update `config.json`, take effect without restart; `/status`, `/check` (force a poll now), `/help`. Bot ignores everyone except the owner chat id.
  *Check:* all 4 commands driven live from the owner's Telegram — `/help`, `/status`, `/check` correct; `/watch gleamflux` (plain username) and `/watch https://www.instagram.com/magshimim_confessions/` (profile URL) both switched targets correctly and baselined silently — done. Bonus: two real (non-simulated) new stories on `@gleamflux` were caught and delivered by the live scheduled job during testing.

- [x] **Step 5 — Hardening**
  Detect expired/invalid Instagram session → warn the owner on Telegram instead of crashing; escalating backoff + owner warning on repeated fetch failures (rate-limit signature); per-item retry-safe notification sending; rotating file logs in `logs/`; global error handler on the Application so no unhandled exception can crash the process silently.
  *Check:* renamed the real session file to simulate expiry (zero live Instagram calls — pure local file-not-found path) → `poll_once` caught it, sent the owner a warning with recovery instructions on Telegram, set a 1h backoff, returned normally without crashing — done. File restored afterward.

- [x] **Step 6 — Run forever on Windows**
  Auto-start at logon via Task Scheduler; final README polish.
  *Check:* registered scheduled task "InstaGraber" (`run_bot.bat` → `pythonw bot.py`), trigger `MSFT_TaskLogonTrigger` (at logon), `ExecutionTimeLimit=PT0S` (unlimited — the default 3-day limit would have killed a 24/7 process), auto-restart up to 5× on crash with a 5 min gap — confirmed via `Get-ScheduledTask`. **Not yet confirmed across an actual logoff/logon cycle** — deliberately not started yet, since `gleamflux` is still cooling down from the Session 2e rate-limit; will fire on the next real logon or can be started manually with `Start-ScheduledTask -TaskName InstaGraber` once the account's confirmed healthy.
