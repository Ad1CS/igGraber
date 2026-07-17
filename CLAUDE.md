# InstaGraber — Instagram Story → Telegram Notifier

Personal bot that watches one Instagram account for new stories and notifies the owner on Telegram. The watched account is changeable at runtime.

## Read these first, every session
1. `ROADMAP.md` — build plan; checkboxes show exactly where we are.
2. `PROJECT_LOG.md` — per-session log of what was done, decisions made, and what's next. Newest entry on top.

## Architecture
- Python (3.14 on this machine), two source files max:
  - `bot.py` — entry point: python-telegram-bot application + repeating poll job + owner commands.
  - `ig_watcher.py` — instaloader wrapper: fetch active story items for the target account.
- `config.json` — runtime-changeable settings (target account, poll interval). The Telegram command `/watch <username>` rewrites it; committed to git.
- `state.json` — ids of already-notified stories. Gitignored.
- `.env` — secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `IG_LOGIN_USERNAME`. Gitignored.

## Hard constraints (do not "simplify" these away)
- Instagram stories **cannot be fetched anonymously** — an authenticated instaloader session is required. The user creates it themselves with `instaloader --login <username>` (interactive password/2FA); it's stored under `%LOCALAPPDATA%\Instaloader\`. Code loads it with `load_session_from_file`.
- Recommend a **secondary** IG account for the login and a modest poll interval (default 15 min) — aggressive polling risks Instagram blocking the account.
- The bot must only respond to and notify `TELEGRAM_CHAT_ID` (the owner). Ignore all other chats.
- Never ask the user to paste passwords/tokens into the chat — they edit `.env` themselves.

## Workflow rules, every session
1. Follow ROADMAP.md step by step. A step is done only after its check actually passes (run the code / send the message — don't assume).
2. After each verified step: tick the roadmap checkbox → append a PROJECT_LOG.md entry (date, changes, decisions, next) → `git commit` → `git push`.
3. Never commit: `.env`, `state.json`, `session-*`, `logs/`, downloaded media. Check `git status` before every commit.
4. Commit messages: `Step N: <what>`.

## Run
```
pip install -r requirements.txt
python bot.py
```
