# Project Log

Newest entry first. Every completed step gets an entry: what changed, decisions made, what's next. This file + ROADMAP.md are how a fresh session catches up on the whole project.

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
