import json
import logging
from typing import Any, Dict, List
from mcp.server.mcpserver import MCPServer
from database import SessionLocal
from models.candidate import Candidate
from models.resume import Resume

logger = logging.getLogger(__name__)

# Initialize official Model Context Protocol (MCP) server
mcp_server = MCPServer("candidate-service")


@mcp_server.tool()
async def get_candidates_with_resumes(user_id: int) -> str:
    """
    Get all candidates belonging to the user, including the count and details
    of all resumes created or uploaded for each candidate.
    """
    db = SessionLocal()
    try:
        candidates = (
            db.query(Candidate)
            .filter(Candidate.user_id == user_id)
            .order_by(Candidate.created_at.desc())
            .all()
        )

        candidate_data = []
        total_resumes_count = 0

        for c in candidates:
            resumes = c.resumes or []
            resume_count = len(resumes)
            total_resumes_count += resume_count

            resume_items = [
                {
                    "resume_id": r.resume_id,
                    "file_name": r.file_name,
                    "file_size_kb": round(r.file_size / 1024, 1) if r.file_size else 0,
                    "uploaded_at": r.uploaded_at.strftime("%Y-%m-%d %H:%M") if r.uploaded_at else "N/A"
                }
                for r in resumes
            ]

            candidate_data.append({
                "candidate_id": c.candidate_id,
                "full_name": c.full_name,
                "email": c.email_address or "N/A",
                "contact_no": c.contact_no or "N/A",
                "resumes_created_count": resume_count,
                "resumes": resume_items,
                "skills": [cs.skill.skill_name for cs in c.candidate_skills if cs.skill] if c.candidate_skills else [],
                "total_experience_records": len(c.experiences or []),
                "qualifications": [q.degree for q in (c.qualifications or []) if q.degree]
            })

        payload = {
            "user_id": user_id,
            "total_candidates": len(candidates),
            "total_resumes_created": total_resumes_count,
            "candidates": candidate_data
        }

        return json.dumps(payload, indent=2)
    finally:
        db.close()


@mcp_server.tool()
async def get_candidate_resume_chart_data(user_id: int) -> str:
    """
    Retrieve aggregated chart-ready statistics of candidate resume distribution for visualization.
    Returns candidate labels, resume counts, and high-level summary metrics.
    """
    db = SessionLocal()
    try:
        candidates = (
            db.query(Candidate)
            .filter(Candidate.user_id == user_id)
            .order_by(Candidate.full_name.asc())
            .all()
        )

        chart_items = []
        total_resumes = 0
        most_active_candidate = None
        max_resumes = 0

        for c in candidates:
            r_count = len(c.resumes or [])
            total_resumes += r_count
            if r_count > max_resumes:
                max_resumes = r_count
                most_active_candidate = c.full_name

            chart_items.append({
                "label": c.full_name,
                "value": r_count,
                "candidate_id": c.candidate_id,
                "email": c.email_address or ""
            })

        chart_payload = {
            "chart_type": "bar",
            "title": "Resumes Created per Candidate",
            "items": chart_items,
            "summary": {
                "total_candidates": len(candidates),
                "total_resumes": total_resumes,
                "most_active_candidate": most_active_candidate or "None",
                "max_resumes": max_resumes,
                "average_resumes_per_candidate": round(total_resumes / max(len(candidates), 1), 2)
            }
        }

        return json.dumps(chart_payload, indent=2)
    finally:
        db.close()


def get_mcp_openai_tools() -> List[Dict[str, Any]]:
    """
    Format MCP Server tools into OpenAI/Groq compatible tool definitions.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_candidates_with_resumes",
                "description": "Get all candidates belonging to the user with their resume count and resume file details",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "integer",
                            "description": "The ID of the user requesting candidate data"
                        }
                    },
                    "required": ["user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_candidate_resume_chart_data",
                "description": "Get visual chart data and statistics showing the count of resumes created for each candidate",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "integer",
                            "description": "The ID of the user requesting chart data"
                        }
                    },
                    "required": ["user_id"]
                }
            }
        }
    ]


async def execute_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """
    Execute a tool call using the MCP server.
    """
    call_res = await mcp_server.call_tool(tool_name, arguments)
    if call_res and call_res.content:
        first = call_res.content[0]
        if hasattr(first, "text"):
            return first.text
        return str(first)
    return "{}"
