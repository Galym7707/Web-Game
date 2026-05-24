"""In-memory room state, role assignment, and scoring for Prompt Gallery."""
import random
import string
import time
import threading

from .artwork import get_random_artwork
from .content import generate_artwork_game_content

ROOM_TTL_SECONDS = 6 * 60 * 60
MAX_STATEMENT_LEN = 180

rooms = {}
_lock = threading.Lock()

ROLE_CURATOR = "curator"
ROLE_AI = "ai_defender"
ROLE_CRITIC = "fake_critic"

ROLE_LABELS = {
    ROLE_CURATOR: "Real Curator",
    ROLE_AI: "AI Defender",
    ROLE_CRITIC: "Fake Critic",
}


def _code():
    return "".join(random.choices(string.ascii_uppercase, k=4))


def _pid():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=12))


def cleanup_old_rooms():
    now = time.time()
    with _lock:
        stale = [c for c, r in rooms.items() if now - r["created_at"] > ROOM_TTL_SECONDS]
        for c in stale:
            del rooms[c]


def create_room(nickname: str):
    cleanup_old_rooms()
    with _lock:
        code = _code()
        while code in rooms:
            code = _code()
        host_id = _pid()
        rooms[code] = {
            "code": code,
            "host_id": host_id,
            "players": [{"id": host_id, "name": nickname[:24] or "Host"}],
            "phase": "lobby",
            "artwork": None,
            "generated_content": None,
            "roles": {},
            "private_tasks": {},
            "submissions": {},
            "statement_order": [],
            "votes": {},
            "scores": {host_id: 0},
            "round_scores": {},
            "reveal": None,
            "created_at": time.time(),
            "round_number": 0,
        }
        return code, host_id


def join_room(code: str, nickname: str):
    with _lock:
        room = rooms.get(code)
        if not room:
            return None, "Room not found"
        if room["phase"] != "lobby":
            return None, "Game already started"
        if len(room["players"]) >= 8:
            return None, "Room is full"
        pid = _pid()
        room["players"].append({"id": pid, "name": nickname[:24] or "Player"})
        room["scores"][pid] = 0
        return pid, None


def _assign_roles(room):
    players = [p["id"] for p in room["players"]]
    random.shuffle(players)
    roles = {}
    roles[players[0]] = ROLE_CURATOR
    roles[players[1]] = ROLE_AI
    for pid in players[2:]:
        roles[pid] = ROLE_CRITIC
    room["roles"] = roles


def _build_private_tasks(room):
    content = room["generated_content"]
    tasks = {}
    for pid, role in room["roles"].items():
        if role == ROLE_CURATOR:
            tasks[pid] = {
                "role": role,
                "role_label": ROLE_LABELS[role],
                "headline": "You are the Real Curator.",
                "instructions": (
                    "You know what this artwork is really about. Write a short "
                    "interpretation in your own words so players believe you are the curator."
                ),
                "curator_notes": content["curator_notes"],
            }
        elif role == ROLE_AI:
            tasks[pid] = {
                "role": role,
                "role_label": ROLE_LABELS[role],
                "headline": "You are the AI Defender.",
                "instructions": (
                    "Below is an AI-generated interpretation. Rewrite it in your own "
                    "voice so nobody guesses it came from an AI."
                ),
                "ai_statement": content["ai_statement"],
            }
        else:
            tasks[pid] = {
                "role": role,
                "role_label": ROLE_LABELS[role],
                "headline": "You are a Fake Critic.",
                "instructions": (
                    "You have no idea what the artwork truly means. Invent a believable "
                    "interpretation that could pass as the real curator's."
                ),
                "mood_words": content["mood_words"],
                "visual_anchors": content["visual_anchors"],
            }
    room["private_tasks"] = tasks


def start_round(code: str, player_id: str):
    with _lock:
        room = rooms.get(code)
        if not room:
            return "Room not found"
        if room["host_id"] != player_id:
            return "Only the host can start"
        if len(room["players"]) < 3:
            return "Need at least 3 players"
        if room["phase"] not in ("lobby", "reveal"):
            return "Round already in progress"

    # Fetch artwork + content outside the lock (network calls).
    artwork = get_random_artwork()
    content = generate_artwork_game_content(artwork)

    with _lock:
        room = rooms.get(code)
        if not room:
            return "Room not found"
        room["artwork"] = artwork
        room["generated_content"] = content
        room["submissions"] = {}
        room["votes"] = {}
        room["statement_order"] = []
        room["reveal"] = None
        room["round_scores"] = {}
        room["round_number"] += 1
        _assign_roles(room)
        _build_private_tasks(room)
        room["phase"] = "writing"
        return None


def submit_statement(code: str, player_id: str, text: str):
    with _lock:
        room = rooms.get(code)
        if not room:
            return "Room not found"
        if room["phase"] != "writing":
            return "Not in writing phase"
        if player_id not in room["roles"]:
            return "Player not in this round"
        text = (text or "").strip()
        if not text:
            return "Statement cannot be empty"
        room["submissions"][player_id] = text[:MAX_STATEMENT_LEN]

        if len(room["submissions"]) == len(room["players"]):
            order = list(room["submissions"].keys())
            random.shuffle(order)
            room["statement_order"] = order
            room["phase"] = "voting"
        return None


def submit_vote(code: str, player_id: str, real: str, ai: str, bluff: str):
    with _lock:
        room = rooms.get(code)
        if not room:
            return "Room not found"
        if room["phase"] != "voting":
            return "Not in voting phase"
        if player_id not in room["roles"]:
            return "Player not in this round"

        order = room["statement_order"]
        own_index = order.index(player_id) if player_id in order else -1

        def valid(idx):
            return isinstance(idx, int) and 0 <= idx < len(order) and idx != own_index

        if not (valid(real) and valid(ai) and valid(bluff)):
            return "Invalid vote (you cannot vote for your own card)"

        room["votes"][player_id] = {"real": real, "ai": ai, "bluff": bluff}

        if len(room["votes"]) == len(room["players"]):
            _score_round(room)
            room["phase"] = "reveal"
        return None


def _score_round(room):
    order = room["statement_order"]
    roles = room["roles"]
    votes = room["votes"]

    # index -> author player_id
    author_of = {i: pid for i, pid in enumerate(order)}
    index_of = {pid: i for i, pid in enumerate(order)}

    curator_id = next(pid for pid, r in roles.items() if r == ROLE_CURATOR)
    ai_id = next(pid for pid, r in roles.items() if r == ROLE_AI)
    curator_idx = index_of[curator_id]
    ai_idx = index_of[ai_id]

    # Tallies
    real_votes = {}   # idx -> count of "this is the real curator"
    ai_votes = {}     # idx -> count of "this is AI"
    bluff_votes = {}  # idx -> count of "best bluff"
    for v in votes.values():
        real_votes[v["real"]] = real_votes.get(v["real"], 0) + 1
        ai_votes[v["ai"]] = ai_votes.get(v["ai"], 0) + 1
        bluff_votes[v["bluff"]] = bluff_votes.get(v["bluff"], 0) + 1

    # Best bluff winner: most bluff votes, tie-break by lowest index.
    bluff_winner_idx = None
    if bluff_votes:
        best = max(bluff_votes.values())
        bluff_winner_idx = min(i for i, c in bluff_votes.items() if c == best)

    delta = {p["id"]: 0 for p in room["players"]}

    # Real Curator: +2 per player who voted their card as real curator.
    delta[curator_id] += 2 * real_votes.get(curator_idx, 0)

    # AI Defender: +2 per player who did NOT identify their card as AI.
    not_ai = len(votes) - ai_votes.get(ai_idx, 0)
    delta[ai_id] += 2 * not_ai
    # +1 bonus if at least one player thought the AI card was the real curator.
    if real_votes.get(ai_idx, 0) >= 1:
        delta[ai_id] += 1

    # Fake Critics: +2 per player who voted their fake as real curator.
    for pid, role in roles.items():
        if role == ROLE_CRITIC:
            idx = index_of[pid]
            delta[pid] += 2 * real_votes.get(idx, 0)

    # Best bluff winner author: +1 (only meaningful for a fake critic, but
    # award to whoever owns the winning card).
    if bluff_winner_idx is not None:
        delta[author_of[bluff_winner_idx]] += 1

    # All players: detection + crowd bonuses.
    for voter_id, v in votes.items():
        if v["real"] == curator_idx:
            delta[voter_id] += 1
        if v["ai"] == ai_idx:
            delta[voter_id] += 1
        if bluff_winner_idx is not None and v["bluff"] == bluff_winner_idx:
            delta[voter_id] += 1

    for pid, d in delta.items():
        room["scores"][pid] = room["scores"].get(pid, 0) + d
    room["round_scores"] = delta

    # Build reveal payload.
    name_of = {p["id"]: p["name"] for p in room["players"]}
    cards = []
    for i, pid in enumerate(order):
        cards.append({
            "letter": chr(65 + i),
            "index": i,
            "text": room["submissions"][pid],
            "author_id": pid,
            "author_name": name_of[pid],
            "role": roles[pid],
            "role_label": ROLE_LABELS[roles[pid]],
            "real_votes": real_votes.get(i, 0),
            "ai_votes": ai_votes.get(i, 0),
            "bluff_votes": bluff_votes.get(i, 0),
            "is_real_curator": i == curator_idx,
            "is_ai": i == ai_idx,
            "is_best_bluff": i == bluff_winner_idx,
        })

    room["reveal"] = {
        "cards": cards,
        "curator_index": curator_idx,
        "ai_index": ai_idx,
        "best_bluff_index": bluff_winner_idx,
        "critic_review": room["generated_content"]["critic_review"],
        "artwork": room["artwork"],
        "round_scores": delta,
    }


def reset_room(code: str, player_id: str):
    with _lock:
        room = rooms.get(code)
        if not room:
            return "Room not found"
        if room["host_id"] != player_id:
            return "Only the host can reset"
        room["phase"] = "lobby"
        room["artwork"] = None
        room["generated_content"] = None
        room["roles"] = {}
        room["private_tasks"] = {}
        room["submissions"] = {}
        room["statement_order"] = []
        room["votes"] = {}
        room["reveal"] = None
        room["round_scores"] = {}
        return None


def get_state(code: str, player_id: str):
    with _lock:
        room = rooms.get(code)
        if not room:
            return None
        phase = room["phase"]
        scores_named = [
            {"id": p["id"], "name": p["name"], "score": room["scores"].get(p["id"], 0)}
            for p in room["players"]
        ]
        scores_named.sort(key=lambda s: s["score"], reverse=True)

        state = {
            "code": code,
            "phase": phase,
            "round_number": room["round_number"],
            "is_host": player_id == room["host_id"],
            "host_id": room["host_id"],
            "players": [{"id": p["id"], "name": p["name"]} for p in room["players"]],
            "player_count": len(room["players"]),
            "scores": scores_named,
            "you": {"id": player_id},
        }

        if phase in ("writing", "voting", "reveal") and room["artwork"]:
            content = room["generated_content"] or {}
            state["artwork"] = {
                "image_url": room["artwork"]["image_url"],
                "exhibition_title": content.get("exhibition_title", "Untitled Exhibition"),
                "source": room["artwork"]["source"],
            }

        # Private role info (never leak others' roles before reveal).
        if phase in ("writing", "voting", "reveal"):
            state["your_task"] = room["private_tasks"].get(player_id)
            state["your_role"] = room["roles"].get(player_id)
            state["submitted"] = player_id in room["submissions"]
            state["submitted_count"] = len(room["submissions"])

        if phase == "voting":
            order = room["statement_order"]
            own_index = order.index(player_id) if player_id in order else -1
            state["statements"] = [
                {"letter": chr(65 + i), "index": i,
                 "text": room["submissions"][pid], "is_yours": i == own_index}
                for i, pid in enumerate(order)
            ]
            state["voted"] = player_id in room["votes"]
            state["voted_count"] = len(room["votes"])

        if phase == "reveal":
            state["reveal"] = room["reveal"]
            content = room["generated_content"] or {}
            state["artwork_meta"] = {
                "title": room["artwork"]["title"],
                "artist": room["artwork"]["artist"],
                "date": room["artwork"]["date"],
                "source": room["artwork"]["source"],
            }
            state["content_source"] = content.get("source", "fallback")

        return state
