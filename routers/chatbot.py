from fastapi import APIRouter, Depends, HTTPException
from models.user import User
from schemas.chatbot import (
    ChatHistoryItem,
    ChatMessageRequest,
    ChatMessageResponse,
    SessionHistoryResponse,
)
from services.chatbot_service import (
    clear_session,
    get_session_history,
    process_chat_message,
)
from utils.auth import get_current_user

router = APIRouter(
    prefix="/chatbot",
    tags=["Chatbot"]
)


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    payload: ChatMessageRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        session_id, reply, chart_data, tool_called = await process_chat_message(
            user_id=current_user.user_id,
            user_message=payload.message,
            session_id=payload.session_id,
        )

        return ChatMessageResponse(
            session_id=session_id,
            reply=reply,
            chart_data=chart_data,
            tool_called=tool_called,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chatbot failed to process message: {str(e)}"
        )


@router.get("/history/{session_id}", response_model=SessionHistoryResponse)
def get_history(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    messages_raw = get_session_history(session_id)
    items = []
    for m in messages_raw:
        items.append(
            ChatHistoryItem(
                role=m.get("role", "user"),
                content=m.get("content", ""),
                timestamp=m.get("timestamp", ""),
                chart_data=m.get("chart_data")
            )
        )
    return SessionHistoryResponse(
        session_id=session_id,
        messages=items
    )


@router.delete("/session/{session_id}")
def reset_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    success = clear_session(session_id)
    return {
        "message": "Session reset successfully" if success else "Session not found",
        "session_id": session_id,
        "cleared": success
    }
