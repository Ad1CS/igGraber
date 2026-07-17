# igGraber (InstaGraber)

Telegram bot that pings you when a watched Instagram account posts a new story. The watched account is changeable at any time with a Telegram command.

- Watched account + poll interval live in `config.json`; change the account live with `/watch <username>`.
- Requires a **logged-in Instagram session** (stories are not visible anonymously). Use a spare account — automated polling is against Instagram's ToS and aggressive use can get the login account blocked.

## Setup
1. `pip install -r requirements.txt`
2. Copy `.env.example` → `.env` and fill it in. **Never commit `.env`.**
3. Telegram: talk to **@BotFather** → `/newbot` → put the token in `.env`. Then open your new bot and press **Start** once.
4. Instagram: `instaloader --login <your_secondary_account>` (interactive login, saves a reusable session).
5. `python bot.py`

## Project docs
- [ROADMAP.md](ROADMAP.md) — build plan and progress
- [PROJECT_LOG.md](PROJECT_LOG.md) — session/decision log
- [CLAUDE.md](CLAUDE.md) — working rules for AI coding sessions
