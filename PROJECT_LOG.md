# Project Log

Newest entry first. Every completed step gets an entry: what changed, decisions made, what's next. This file + ROADMAP.md are how a fresh session catches up on the whole project.

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
