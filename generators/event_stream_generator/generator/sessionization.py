from __future__ import annotations


def session_id_for(user_id: int, bucket: int) -> str:
    return f"s_{user_id}_{bucket}"
