# Project Log

Newest entry first. Every completed step gets an entry: what changed, decisions made, what's next. This file + ROADMAP.md are how a fresh session catches up on the whole project.

---

## 2026-07-18 — Session 2d: Step 4 — runtime commands built & verified live

**Done:** Added owner-only command handlers to [bot.py](bot.py): `owner_only` decorator silently ignores any chat id other than `TELEGRAM_CHAT_ID`. `/watch <username_or_url>` validates via `Profile.from_username` (catches `ProfileNotExistsException`), rewrites `config.json`, and immediately calls `poll_once` to baseline the new target right away rather than waiting for the next scheduled cycle. `/status` reports current target/interval/sync state/known-id count. `/check` forces an immediate poll and reports what happened (baselined / N sent / nothing new). `/help` lists commands. `poll_once` was refactored to return a result dict (`baselined`, `active_count`, `notified_count`, `error`) so the commands can give meaningful replies instead of just "done". Also added `parse_ig_username()` so `/watch` accepts either a bare username or a full `instagram.com/<user>/` profile URL (user specifically asked for URL support) — strips scheme/query, takes the first path segment.

**Verified live**, all real Telegram interactions (not simulated): `/help` → correct command list. `/status` → correct target/interval/"in sync"/0 known ids. `/check` → "Checked — nothing new" (accurate). `/watch gleamflux` (bare username, sent before the URL-parsing code existed) → switched target, baselined silently at 0. After adding URL parsing and restarting: `/watch https://www.instagram.com/magshimim_confessions/` → correctly extracted `magshimim_confessions`, switched target, baselined silently at 0. Along the way, **two real (non-simulated) new stories were posted on `@gleamflux`** during testing and the live scheduled job caught + delivered both automatically (message_id 18 and 22) — incidental but strong end-to-end proof the whole pipeline works for real, not just in controlled tests.

**Operational notes for next session:**
- The bot process needs a manual restart to pick up either code changes or a `poll_interval_minutes` change — it's not hot-reloaded (this becomes moot once Step 6 sets it up as a persistent service).
- **`poll_interval_minutes` was bumped from 15 to 1** at the user's request, for faster testing turnaround. This is more aggressive than the "modest interval" guidance in CLAUDE.md and raises the risk of Instagram flagging the login account — flagged to the user; revisit dialing it back (e.g. 5 min) once things are confirmed stable, before Step 6 makes this run unattended long-term.
- Final target confirmed set back to the real one, `magshimim_confessions`, with a clean empty `state.json` baseline.

**Next:** Step 5 — hardening (expired-session detection/warning, retry/backoff, `logs/` output, exception guarding), then Step 6 (Windows Task Scheduler autostart).

---

## 2026-07-18 — Session 2c: Step 3 — notifier loop built & verified

**Done:** [bot.py](bot.py) added: `poll_once(bot)` is the core logic — loads `config.json`, fetches active stories via `ig_watcher.get_active_stories`, diffs ids against `state.json`. If the target in state doesn't match the configured target (first run, or a switched account), it baselines silently — saves the current ids as already-notified without messaging, so pre-existing stories never spam on startup or on switching accounts. Otherwise it sends a Telegram notification (video or photo, matching `is_video`) for every id not yet in `notified_ids`, then updates state. `send_story_notification` tries the Instagram CDN URL directly (Telegram fetches it server-side); if that ever gets hotlink-blocked, it falls back to downloading the bytes through the authenticated instaloader session and uploading them directly. `scheduled_poll` wraps `poll_once` for `Application.job_queue.run_repeating` on the configured `poll_interval_minutes`. No command handlers yet (Step 4).

**Verified live** with 4 sequential runs (can't wait for a real new post, so simulated deterministically): (1) fresh state against `@instagram` (has a live story) → baselined silently, 0 messages; (2) re-run, unchanged → 0 messages; (3) manually cleared `notified_ids` to simulate a new story → exactly 1 notification sent and confirmed delivered (HTTP 200, `message_id=3`, sent as video via direct CDN URL — no fallback needed); (4) reverted `config.json` to the real target `magshimim_confessions` → baselined silently at 0 (correct, nothing currently posted), leaving a clean production `state.json`.

**Next:** Step 4 — add owner-only command handlers to `bot.py`: `/watch <username>` (validate the account exists via `Profile.from_username`, rewrite `config.json`, takes effect on the next poll without restart), `/status`, `/check` (force an immediate poll), `/help`. Reject/ignore any chat id other than `TELEGRAM_CHAT_ID`.

---

## 2026-07-18 — Session 2b: Step 2 — story fetcher built & verified

**Done:** [ig_watcher.py](ig_watcher.py) added: `load_session(username)` wraps `load_session_from_file`; `get_active_stories(L, target_username)` resolves the profile, calls `L.get_stories(userids=[profile.userid])`, flattens each story's items into dicts (`id`, `timestamp`, `is_video`, `url`), sorted oldest-first. Tested manually against `magshimim_confessions` (0 active stories — correct, nothing posted since we started) and `instagram` (1 active item, all fields populated correctly) — confirms the parsing logic itself works, not just that the target account happens to be empty right now.

**Note:** stories work with the public account `magshimim_confessions` via `get_stories(userids=[...])` even though `gleamflux` does not follow it — confirms the earlier assumption that public-account stories don't require a follow relationship, just any logged-in session.

**Next:** Step 3 — the notifier loop in `bot.py`: repeating poll job, diff fetched story ids against `state.json`, send new ones to Telegram (media attached where possible), baseline silently on first run for a new target so old stories don't spam on startup.

---

## 2026-07-18 — Session 2: Step 1 complete — both credentials verified

**Done:** Telegram: user pressed Start on @igGraberBOT, re-sent test message → delivered successfully (chat id 7743200994 confirmed correct). Instagram: plain `instaloader --login gleamflux` failed with `"fail" status, message "Unexpected null login result"` — an Instagram-side checkpoint/suspicious-login response on a fresh secondary account, not a wrong password (confirmed instaloader was already latest, 4.15.2). Worked around it via `instaloader --load-cookies=chrome` (after logging into instagram.com as `gleamflux` normally in Chrome first) — this imports an already-authenticated browser session instead of doing instaloader's own API login, which avoided the checkpoint entirely. Session saved to `%LOCALAPPDATA%\Instaloader\session-gleamflux`. Installed `browser_cookie3` (one-time setup dependency only, not added to requirements.txt — the running bot only ever calls `load_session_from_file`, it doesn't need this package). `IG_LOGIN_USERNAME=gleamflux` set in `.env`. Verified end-to-end with a script that loads the session and fetches the `magshimim_confessions` profile (1,461 followers) — confirms both auth and target-account visibility work together.

**Decision:** if a fresh IG login ever hits the same "Unexpected null login result" checkpoint again (e.g. re-doing this on a new secondary account later), skip straight to the `--load-cookies=<browser>` workaround rather than retrying plain `--login` — it's faster and didn't trigger the checkpoint.

**Next:** Step 2 — build `ig_watcher.py`: given `target_username` from `config.json`, return the account's currently active story items (id, timestamp, media type/URL) using the saved `gleamflux` session.

---

## 2026-07-17 — Session 1c: Telegram token in, verified live

**Done:** User created the bot via @BotFather — **@igGraberBOT** (id `8816428327`) — and gave the token, which is now saved only in `.env` (confirmed git-ignored via `git check-ignore`, never committed). `getMe` call confirms the token is valid. First `sendMessage` test returned `400 chat not found` — expected, since the user hadn't pressed Start on the bot yet. Waiting on that before the send-test can pass.

**Next:** user presses Start on @igGraberBOT in Telegram → re-run the test send → once it arrives, Step 1's Telegram half is done. Still need the Instagram session (`instaloader --login`) for the other half of Step 1.

---

## 2026-07-17 — Session 1b: pushed to GitHub, deps installed

**Done:** `pip install -r requirements.txt` succeeded (Python 3.14, no pins needed). Remote repo already existed at https://github.com/Ad1CS/igGraber.git (user-created, had an auto-generated "Initial commit" with a one-line README). Added it as `origin`, rebased our Step 0 commit on top, resolved the README.md add/add conflict by keeping our fuller version titled "# igGraber (InstaGraber)", pushed to `main`. No `gh` CLI needed — Windows already had Git Credential Manager (`credential.helper=manager`) configured, so the HTTPS push authenticated via a normal browser popup.

**Still blocked on user action (cannot be done by the assistant — involves entering the user's own credentials):**
- **Telegram bot token:** must be created by messaging **@BotFather** in Telegram directly (no tool access to the user's Telegram account) and the token pasted into `.env` by the user.
- **Instagram session:** `instaloader --login <username>` prompts interactively for a password (and 2FA) — entering account passwords is something the assistant must never do, even at the user's request. The user needs to run this themselves in a terminal in this folder.

**Next:** once the user has done those two things (`.env` filled in, IG session file exists), verify Step 1 (send a test Telegram message, load the IG session), commit+push, then build Step 2 (story fetcher).

---

## 2026-07-17 — Session 1: kickoff & scaffold (Step 0)

**Done:** Project scaffolded from an empty folder — docs (CLAUDE.md, ROADMAP.md, this log, README.md), `.gitignore`, `.env.example` (+ local `.env` pre-filled with the owner chat id), `config.json`, `requirements.txt`. Git repo initialized on `main`, first commit made. GitHub push pending: `gh` CLI wasn't installed, so the user needs to install it and run `gh auth login` once; then we create the private repo and push.

**Decisions:**
- Stack: Python + **instaloader** for Instagram + **python-telegram-bot** for Telegram + `.env` for secrets. Reason: stories are only visible to logged-in sessions, and instaloader is the mature way to use one from Python.
- Target account lives in `config.json` (currently `magshimim_confessions`) and will be changeable live via a `/watch <username>` Telegram command — no restart, no code edit.
- Poll every 15 minutes by default (configurable). Modest on purpose: lowers the risk of Instagram flagging the login account. Recommended to log in with a secondary IG account, not the user's main one.
- The bot only obeys/notifies the owner chat id, which is stored in `.env` (not in committed files).
- GitHub repo will be **private** (personal automation; no reason to publish).
- Machine runs Python 3.14 — if a dependency doesn't support it yet at install time, we pin an older major version in requirements.txt during Step 1's check.

**Next — user actions (Step 1 prerequisites):**
1. Telegram: @BotFather → `/newbot` → copy the token into `.env`; then open the new bot and press **Start** once (otherwise it can't message you).
2. `pip install -r requirements.txt`
3. Instagram: `instaloader --login <secondary_account>` in a terminal (interactive; also set `IG_LOGIN_USERNAME` in `.env` to the same username).
4. GitHub: install GitHub CLI (`winget install GitHub.cli`), then `gh auth login`.

**Next — build:** verify Step 1 (test Telegram send + session load), commit+push Step 0 & 1, then Step 2 (story fetcher).
