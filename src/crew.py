import json
from crewai import Crew, Process, Task

from src.agents import build_agents


FINAL_JSON_INSTRUCTIONS = """
Return ONLY a JSON array (no markdown fences, no prose before or after).
Each item must be an object with exactly these fields:
- "keyword": string
- "market": string (country name)
- "language": string (ISO code, e.g. "en", "de")
- "intent": one of "informational", "commercial", "transactional", "navigational"
- "platform": one of "Google (SEO)", "Google Shopping / Ads", "Pinterest", "Instagram", "TikTok", "Etsy"
- "cluster": short string grouping this keyword with related ones (e.g. "Art Deco armchairs")
- "priority": integer 1-5 (5 = highest opportunity: clear buyer intent + fits the niche tightly)
"""


def build_crew(profile: dict) -> Crew:
    agents = build_agents()

    categories = ", ".join(profile["categories"])
    markets = ", ".join(f"{m['country']} ({m['language']})" for m in profile["markets"])
    platforms = ", ".join(profile["platforms"])

    task_breakdown = Task(
        description=(
            f"Client business: {profile['business_description']}\n\n"
            f"Rough category list given: {categories}\n"
            f"Target markets: {markets}\n\n"
            "Produce a refined list of 8-14 tightly-defined sub-niches "
            "(e.g. not 'furniture' but 'mirrored Art Deco console tables'), "
            "plus 2-3 buyer personas describing who searches for this and "
            "why (gift buyer, interior designer, homeowner redecorating, etc). "
            "Write this as plain text, clearly organized."
        ),
        expected_output="A refined sub-niche list and buyer personas as plain text.",
        agent=agents["vertical_strategist"],
    )

    task_keywords = Task(
        description=(
            f"Using the sub-niches and personas above, generate keywords for "
            f"EVERY target market ({markets}), in the correct local language "
            "for each market — not machine-translated, but how a native "
            "shopper would actually search. For each market produce a mix of: "
            "- 5+ short-tail keywords (2-3 words)\n"
            "- 8+ long-tail keywords (4+ words, specific style/material/room)\n"
            "Cover style descriptors (Art Deco, Gatsby, glam, velvet, gold "
            "metal), product types, and room/use-case context. "
            "List them as plain text grouped by market, ready for the next "
            "step to structure and score."
        ),
        expected_output="A plain-text list of keywords grouped by market/language.",
        agent=agents["keyword_researcher"],
        context=[task_breakdown],
    )

    task_platforms = Task(
        description=(
            f"For the keyword list above, assign each keyword (or clearly "
            f"note it applies to a cluster) the single best-fit platform from: "
            f"{platforms}. Inspirational/visual style searches (e.g. 'art deco "
            "living room ideas') usually fit Pinterest/Instagram/TikTok; "
            "specific product searches with buying intent usually fit Google "
            "SEO or Google Shopping/Ads; handmade/vintage-style niche terms "
            "can fit Etsy. Briefly justify non-obvious picks."
        ),
        expected_output="The keyword list annotated with a platform and short rationale per keyword.",
        agent=agents["platform_strategist"],
        context=[task_keywords],
    )

    task_final = Task(
        description=(
            "Take everything from the previous steps and produce the final "
            "deliverable. Deduplicate near-identical keywords, group into "
            "clusters, assign search intent and a 1-5 priority score.\n\n"
            f"{FINAL_JSON_INSTRUCTIONS}"
        ),
        expected_output="A raw JSON array matching the specified schema, nothing else.",
        agent=agents["editor"],
        context=[task_breakdown, task_keywords, task_platforms],
    )

    return Crew(
        agents=list(agents.values()),
        tasks=[task_breakdown, task_keywords, task_platforms, task_final],
        process=Process.sequential,
        verbose=False,
    )


def run_keyword_research(profile: dict) -> list[dict]:
    """Runs the crew and returns a parsed list of keyword dicts.

    Falls back to wrapping raw text if the model doesn't return clean JSON.
    """
    crew = build_crew(profile)
    result = crew.kickoff()
    raw = str(result)

    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    # Fallback: surface the raw text so nothing is silently lost
    return [{
        "keyword": "PARSE_ERROR_SEE_RAW_OUTPUT",
        "market": "",
        "language": "",
        "intent": "",
        "platform": "",
        "cluster": "raw_output",
        "priority": 0,
        "raw": raw,
    }]
