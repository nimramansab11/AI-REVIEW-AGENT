
import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

load_dotenv()


# -----------------------------
# STATE
# -----------------------------

class ReviewerState(TypedDict):
    content: str
    content_review: str
    grammar_review: str
    structure_review: str
    final_review: str


# -----------------------------
# LLM
# -----------------------------

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY is missing. Add it to your .env file."
    )


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.2,
    api_key=api_key,
)


# -----------------------------
# CONTENT REVIEWER
# -----------------------------

def content_reviewer(state: ReviewerState):

    prompt = f"""
You are a Content Reviewer Agent.

Analyze the following content.

Focus ONLY on:
- Accuracy and relevance
- Completeness
- Quality of ideas
- Missing information
- Strengths of the content

Do not focus on grammar.

CONTENT:
{state["content"]}
"""

    response = llm.invoke(prompt)

    return {
        "content_review": response.content
    }


# -----------------------------
# GRAMMAR REVIEWER
# -----------------------------

def grammar_reviewer(state: ReviewerState):

    prompt = f"""
You are a Grammar Reviewer Agent.

Review the following content.

Focus ONLY on:
- Grammar
- Spelling
- Sentence construction
- Word usage
- Clarity of sentences

Give specific examples of mistakes and corrections.

CONTENT:
{state["content"]}
"""

    response = llm.invoke(prompt)

    return {
        "grammar_review": response.content
    }


# -----------------------------
# STRUCTURE REVIEWER
# -----------------------------

def structure_reviewer(state: ReviewerState):

    prompt = f"""
You are a Structure Reviewer Agent.

Review the following content.

Focus ONLY on:
- Organization
- Logical flow
- Paragraph structure
- Beginning, middle and ending
- Readability
- Overall presentation

Suggest improvements where necessary.

CONTENT:
{state["content"]}
"""

    response = llm.invoke(prompt)

    return {
        "structure_review": response.content
    }


# -----------------------------
# FINAL REVIEWER
# -----------------------------

def final_reviewer(state: ReviewerState):

    prompt = f"""
You are the Final Reviewer Agent.

Create a professional final review using the three specialist
reviews below.

ORIGINAL CONTENT:
{state["content"]}

CONTENT REVIEW:
{state["content_review"]}

GRAMMAR REVIEW:
{state["grammar_review"]}

STRUCTURE REVIEW:
{state["structure_review"]}

Return the final report using exactly these sections:

## Overall Score
Give a score out of 10.

## Strengths
List the strongest parts.

## Content Issues
List important content problems.

## Grammar Issues
List important grammar problems.

## Structure Issues
List important structure problems.

## Improvement Suggestions
Give practical suggestions.

## Final Verdict
Give a short professional conclusion.
"""

    response = llm.invoke(prompt)

    return {
        "final_review": response.content
    }


# -----------------------------
# LANGGRAPH
# -----------------------------

builder = StateGraph(ReviewerState)

builder.add_node("content_reviewer", content_reviewer)
builder.add_node("grammar_reviewer", grammar_reviewer)
builder.add_node("structure_reviewer", structure_reviewer)
builder.add_node("final_reviewer", final_reviewer)


# Start specialist reviews
builder.add_edge(START, "content_reviewer")
builder.add_edge(START, "grammar_reviewer")
builder.add_edge(START, "structure_reviewer")


# All specialist reviews → final reviewer
builder.add_edge("content_reviewer", "final_reviewer")
builder.add_edge("grammar_reviewer", "final_reviewer")
builder.add_edge("structure_reviewer", "final_reviewer")


# Final reviewer → END
builder.add_edge("final_reviewer", END)


reviewer_graph = builder.compile()


# -----------------------------
# RUN AGENT
# -----------------------------

def run_reviewer(content: str) -> str:

    result = reviewer_graph.invoke(
        {
            "content": content,
            "content_review": "",
            "grammar_review": "",
            "structure_review": "",
            "final_review": "",
        }
    )

    return result["final_review"]
