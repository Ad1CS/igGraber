import instaloader


def load_session(ig_login_username: str) -> instaloader.Instaloader:
    L = instaloader.Instaloader()
    L.load_session_from_file(ig_login_username)
    return L


def get_active_stories(L: instaloader.Instaloader, target_username: str) -> list[dict]:
    """Return currently active story items for target_username, oldest first."""
    profile = instaloader.Profile.from_username(L.context, target_username)
    items = []
    for story in L.get_stories(userids=[profile.userid]):
        for item in story.get_items():
            items.append({
                "id": item.mediaid,
                "timestamp": item.date_utc.isoformat(),
                "is_video": item.is_video,
                "url": item.video_url if item.is_video else item.url,
            })
    items.sort(key=lambda i: i["timestamp"])
    return items
