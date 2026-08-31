"""
CrewAI agents for the vertical keyword research pipeline.
"""

import os

from crewai import Agent
from langchain_groq import ChatGroq


def _llm() -> ChatGroq:
    return ChatGroq(
        model=os.environ.get("GROQ_MODEL", "groq/llama-3.3-70b-versatile").removeprefix("groq/"),
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.3,
    )


def build_agents() -> dict[str, Agent]:
    llm = _llm()

    vertical_strategist = Agent(
        role="Vertical Market Strategist",
        goal=(
            "Break down a client's broad product/service offering into "
            "tightly-defined sub-niches and buyer personas that will guide "
            "highly targeted keyword research."
        ),
        backstory=(
            "You are a senior e-commerce strategist who specialises in luxury "
            "home decor and furniture. You excel at identifying micro-segments "
            "within a product catalogue and mapping them to the real motivations "
            "of shoppers — gift buyers, interior designers, homeowners, etc."
        ),
        llm=llm,
        verbose=False,
    )

    keyword_researcher = Agent(
        role="Multilingual Keyword Researcher",
        goal=(
            "Generate native, culturally accurate keyword lists for each "
            "target market using the sub-niches and personas provided."
        ),
        backstory=(
            "You are a multilingual SEO specialist fluent in English, German, "
            "Italian, Spanish, and French. You know exactly how shoppers phrase "
            "their searches in each language — never relying on word-for-word "
            "translation, but producing terms real buyers actually type."
        ),
        llm=llm,
        verbose=False,
    )

    platform_strategist = Agent(
        role="Platform Distribution Strategist",
        goal=(
            "Assign the single most effective platform to each keyword based "
            "on intent, visual appeal, and platform audience fit."
        ),
        backstory=(
            "You are a digital marketing strategist with deep expertise in "
            "Google SEO/Ads, Pinterest, Instagram, TikTok, and Etsy. You "
            "understand which platform maximises visibility for every type of "
            "search query and content format."
        ),
        llm=llm,
        verbose=False,
    )

    editor = Agent(
        role="Keyword Data Editor",
        goal=(
            "Deduplicate, cluster, score, and format all keyword data into a "
            "clean, structured JSON array ready for direct use in campaigns."
        ),
        backstory=(
            "You are a meticulous data editor who transforms raw keyword lists "
            "into perfectly structured, de-duplicated JSON. You never add "
            "commentary — you output only the final JSON array."
        ),
        llm=llm,
        verbose=False,
    )

    return {
        "vertical_strategist": vertical_strategist,
        "keyword_researcher": keyword_researcher,
        "platform_strategist": platform_strategist,
        "editor": editor,
    }
