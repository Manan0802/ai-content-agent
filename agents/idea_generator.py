import json
from typing import Protocol
from orchestrator.state import ContentState
from integrations.groq_client import GroqClient
from prompts.idea_prompts import idea_system_prompt

_SEEDS = {
    "horror": ["Bhoot bangla real story", "Cursed village India", "Haunted railway station"],
    "tech": ["New AI tool 2026", "Phone hidden features", "Coding job future"],
    "finance": ["SIP vs FD", "First salary mistakes", "Credit card trap"],
    "motivation": ["5am discipline", "Failure to comeback", "Stop scrolling"],
    "mythology": ["Mahabharata hidden fact", "Shiva untold story", "Ramayana mystery"],
    "comedy": ["Indian parents logic", "Hostel life", "Online class fails"],
    "trending": ["Today viral news", "Latest meme explained", "Trending challenge"],
}


class TrendsProvider(Protocol):
    def fetch(self, niche: str) -> list[str]: ...


class SeedTrendsProvider:
    def fetch(self, niche: str) -> list[str]:
        return _SEEDS.get(niche, _SEEDS["trending"])


def idea_generator_node(state: ContentState, groq: GroqClient,
                        trends: TrendsProvider) -> ContentState:
    state["status"] = "running"
    try:
        seeds = trends.fetch(state["niche"])
        system = idea_system_prompt(state["niche"], state["language"])
        user = "Trending seed topics:\n- " + "\n- ".join(seeds)
        raw = groq.complete(system=system, user=user, json_mode=True)
        ideas = json.loads(raw).get("ideas", [])
        ideas.sort(key=lambda i: i.get("viral_score", 0), reverse=True)
        state["topic_candidates"] = ideas
    except Exception as e:  # noqa: BLE001 - record, don't crash the pipeline
        state.setdefault("errors", []).append(f"idea_generator: {e}")
        state["topic_candidates"] = []
    return state
