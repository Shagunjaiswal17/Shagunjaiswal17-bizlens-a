from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.chat import ChatQueryRequest, ChatQueryResponse
from ..services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Ask BizLens AI Assistant"])


@router.post("", response_model=ChatQueryResponse, summary="Natural Language Ledger Query")
def chat_with_ledger(req: ChatQueryRequest, db: Session = Depends(get_db)):
    """
    Conversational AI assistant over user's financial documents.
    1. Parses user intent into a safe parameterized query filter via Gemini.
    2. Runs secure SQLAlchemy ORM execution (Zero raw LLM SQL).
    3. Synthesizes an executive reply with clickable document citations.
    """
    safe_filter = ChatService.parse_user_intent(req.message)
    response = ChatService.execute_safe_query(db, safe_filter)
    return response
