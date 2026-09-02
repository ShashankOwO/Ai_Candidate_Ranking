import datetime
import json
import logging
import os
import uuid
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from groq import Groq

from schemas.chatbot import ChartData, ChartItem, ChartSummary
from services.mcp_server import execute_mcp_tool, get_mcp_openai_tools

load_dotenv()

logger = logging.getLogger(__name__)

# Session in-memory storage: session_id -> { "messages": [...], "created_at": ... }
_session_storage: Dict[str, Dict[str, Any]] = {}

SYSTEM_PROMPT = """You are the AI Candidate & Resume Assistant for the AI Candidate Ranking platform.
Your job is to assist recruiters and hiring managers in understanding their candidates and tracking the resumes created or uploaded for them.

You have access to MCP (Model Context Protocol) tools:
1. `get_candidates_with_resumes(user_id)`: Fetches all candidates owned by this user along with their created resumes count, file names, upload dates, skills, and qualifications.
2. `get_candidate_resume_chart_data(user_id)`: Fetches visual chart metrics and resume distribution statistics per candidate.

Guidelines:
- Always be helpful, clear, and professional.
- When asked about candidates, resumes created, who has how many resumes, or resume statistics, CALL the appropriate MCP tool.
- Present candidate information in clean, formatted bullet points or tables.
- Highlight key details such as candidate name, resume count, and key skills.
- If the user asks for a chart, comparison, or breakdown of resumes, invoke `get_candidate_resume_chart_data`.
- Keep answers informative and concise.
"""


def _get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured in the environment")
    return Groq(api_key=api_key)


def get_or_create_session(session_id: Optional[str] = None) -> str:
    if not session_id or session_id not in _session_storage:
        new_id = session_id or str(uuid.uuid4())
        _session_storage[new_id] = {
            "messages": [],
            "created_at": datetime.datetime.now().isoformat(),
            "last_chart": None,
        }
        return new_id
    return session_id


def clear_session(session_id: str) -> bool:
    if session_id in _session_storage:
        del _session_storage[session_id]
        return True
    return False


def get_session_history(session_id: str) -> List[Dict[str, Any]]:
    session = _session_storage.get(session_id)
    if not session:
        return []
    return session.get("messages", [])


def _extract_chart_from_payload(payload_str: str) -> Optional[ChartData]:
    try:
        data = json.loads(payload_str)
        if "items" in data and isinstance(data["items"], list):
            items = [
                ChartItem(
                    label=item.get("label", "Unknown"),
                    value=int(item.get("value", 0)),
                    candidate_id=item.get("candidate_id"),
                    email=item.get("email"),
                )
                for item in data["items"]
            ]
            summary_dict = data.get("summary", {})
            summary = ChartSummary(
                total_candidates=summary_dict.get("total_candidates", len(items)),
                total_resumes=summary_dict.get("total_resumes", sum(i.value for i in items)),
                most_active_candidate=summary_dict.get("most_active_candidate"),
                max_resumes=summary_dict.get("max_resumes", max([i.value for i in items], default=0)),
                average_resumes_per_candidate=summary_dict.get("average_resumes_per_candidate", 0.0),
            )
            return ChartData(
                chart_type=data.get("chart_type", "bar"),
                title=data.get("title", "Resumes per Candidate"),
                items=items,
                summary=summary,
            )
        elif "candidates" in data and isinstance(data["candidates"], list):
            items = [
                ChartItem(
                    label=c.get("full_name", "Unknown"),
                    value=int(c.get("resumes_created_count", 0)),
                    candidate_id=c.get("candidate_id"),
                    email=c.get("email"),
                )
                for c in data["candidates"]
            ]
            total_res = data.get("total_resumes_created", sum(i.value for i in items))
            max_c = max(items, key=lambda x: x.value, default=None)
            summary = ChartSummary(
                total_candidates=len(items),
                total_resumes=total_res,
                most_active_candidate=max_c.label if max_c else None,
                max_resumes=max_c.value if max_c else 0,
                average_resumes_per_candidate=round(total_res / max(len(items), 1), 2),
            )
            return ChartData(
                chart_type="bar",
                title="Resumes Created per Candidate",
                items=items,
                summary=summary,
            )
    except Exception as e:
        logger.warning("Could not extract chart data: %s", e)
    return None


async def process_chat_message(
    user_id: int,
    user_message: str,
    session_id: Optional[str] = None,
) -> Tuple[str, str, Optional[ChartData], Optional[str]]:
    """
    Process incoming user chat message with session memory and MCP tools.
    Returns (session_id, reply_text, chart_data, tool_called).
    """
    active_session_id = get_or_create_session(session_id)
    session = _session_storage[active_session_id]

    # Append user turn to memory
    now_iso = datetime.datetime.now().isoformat()
    session["messages"].append({
        "role": "user",
        "content": user_message,
        "timestamp": now_iso,
    })

    client = _get_groq_client()
    tools = get_mcp_openai_tools()

    # Build dynamic system prompt with user_id injected
    system_prompt = f"""You are the AI Candidate & Resume Assistant for the AI Candidate Ranking platform.
Your job is to assist recruiters and hiring managers in understanding their candidates and tracking the resumes created or uploaded for them.

The currently authenticated user's ID is {user_id}. When calling tools for candidate data or charts, always supply user_id={user_id}. Never ask the user for their user ID.

You have access to MCP (Model Context Protocol) tools:
1. `get_candidates_with_resumes(user_id)`: Fetches all candidates owned by this user along with their created resumes count, file names, upload dates, skills, and qualifications.
2. `get_candidate_resume_chart_data(user_id)`: Fetches visual chart metrics and resume distribution statistics per candidate.

Guidelines:
- Always be helpful, clear, and professional.
- When asked about candidates, resumes created, who has how many resumes, or resume statistics, CALL the appropriate MCP tool immediately using user_id={user_id}.
- Present candidate information in clean, formatted bullet points or markdown tables.
- Highlight key details such as candidate name, resume count, and key skills.
- If the user asks for a chart, comparison, or breakdown of resumes, invoke `get_candidate_resume_chart_data`.
- Keep answers informative and concise.
"""

    # Build context from session history (keep up to last 10 messages for context)
    recent_history = session["messages"][-10:]
    llm_messages = [{"role": "system", "content": system_prompt}]

    for m in recent_history:
        llm_messages.append({"role": m["role"], "content": m["content"]})

    selected_model = "openai/gpt-oss-20b"
    chart_result: Optional[ChartData] = None
    tool_called: Optional[str] = None

    try:
        # Step 1: Call LLM with MCP tools
        response = client.chat.completions.create(
            model=selected_model,
            messages=llm_messages,
            tools=tools,
            tool_choice="auto",
        )
        choice = response.choices[0]
        response_msg = choice.message

        if response_msg.tool_calls:
            # LLM decided to call an MCP tool
            llm_messages.append(response_msg)

            for tool_call in response_msg.tool_calls:
                t_name = tool_call.function.name
                tool_called = t_name

                # Enforce security: always bind the authenticated user_id
                try:
                    args = json.loads(tool_call.function.arguments or "{}")
                except Exception:
                    args = {}
                args["user_id"] = user_id

                # Execute on MCP server
                tool_output = await execute_mcp_tool(t_name, args)

                # Extract chart data if relevant
                chart_data_candidate = _extract_chart_from_payload(tool_output)
                if chart_data_candidate:
                    chart_result = chart_data_candidate
                    session["last_chart"] = chart_data_candidate

                llm_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_output,
                })

            # Step 2: Call LLM with tool output to get final natural language answer
            second_response = client.chat.completions.create(
                model=selected_model,
                messages=llm_messages,
            )
            final_reply = second_response.choices[0].message.content or "Here is the candidate information."
        else:
            final_reply = response_msg.content or "I am here to help with your candidates and resumes."

            lower_msg = user_message.lower()
            # If user asks for chart or data visualization
            if any(w in lower_msg for w in ["chart", "graph", "plot", "distribution", "bar"]):
                if session.get("last_chart"):
                    chart_result = session["last_chart"]
                else:
                    tool_output = await execute_mcp_tool("get_candidate_resume_chart_data", {"user_id": user_id})
                    chart_result = _extract_chart_from_payload(tool_output)
                    if chart_result:
                        session["last_chart"] = chart_result
                        tool_called = "get_candidate_resume_chart_data"
            # If user asked about candidates or resumes but LLM didn't emit a tool_call
            elif any(w in lower_msg for w in ["candidate", "candidates", "resume", "resumes", "applicant", "applicants"]):
                tool_output = await execute_mcp_tool("get_candidates_with_resumes", {"user_id": user_id})
                tool_called = "get_candidates_with_resumes"
                chart_data_candidate = _extract_chart_from_payload(tool_output)
                if chart_data_candidate:
                    chart_result = chart_data_candidate
                    session["last_chart"] = chart_data_candidate

                followup_messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                    {"role": "system", "content": f"Here is the verified data from get_candidates_with_resumes MCP tool: {tool_output}\nPresent this clearly to the user."},
                ]
                try:
                    second_response = client.chat.completions.create(
                        model=selected_model,
                        messages=followup_messages,
                    )
                    if second_response.choices[0].message.content:
                        final_reply = second_response.choices[0].message.content
                except Exception as ex:
                    logger.warning("Followup query failed: %s", ex)

    except Exception as e:
        logger.exception("Error during LLM chat processing: %s", e)
        final_reply = (
            f"I encountered an issue processing your request: {str(e)}. "
            "Please verify your connection and try again."
        )

    # Append assistant response to session memory
    session["messages"].append({
        "role": "assistant",
        "content": final_reply,
        "timestamp": datetime.datetime.now().isoformat(),
        "chart_data": chart_result.model_dump() if chart_result else None,
        "tool_called": tool_called,
    })

    return active_session_id, final_reply, chart_result, tool_called
