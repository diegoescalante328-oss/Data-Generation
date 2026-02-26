from __future__ import annotations

from datetime import datetime, timedelta
from random import Random

from .sessionization import session_id_for


def generate_stream(rows: int, seed: int, late_events: bool = False) -> list[dict]:
    rng = Random(seed)
    start = datetime(2024, 1, 1, 0, 0, 0)
    events = []
    current = start
    for i in range(rows):
        user_id = rng.randint(1, 50)
        current += timedelta(seconds=rng.randint(1, 20))
        event_time = current
        if late_events and rng.random() < 0.05:
            event_time = current - timedelta(seconds=rng.randint(1, 30))
        events.append(
            {
                "event_id": f"e_{i+1}",
                "event_time": event_time.isoformat(),
                "user_id": user_id,
                "session_id": session_id_for(user_id, i // 5),
                "event_type": rng.choice(["view", "click", "purchase"]),
                "metadata": {"page": rng.choice(["/", "/pricing", "/docs"])},
                "source": rng.choice(["web", "mobile"]),
            }
        )
    return events
