from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, File, UploadFile, Form, Depends, Header
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import time
import os
from typing import Optional, List
from datetime import datetime, timezone

from .rag.pipeline import Pipeline
from .rag.ingestor import Ingestor
from app.repositories.chat import chat_repository
from app.models.user import (
    ChatSessionCreate, ChatSessionUpdate, ChatSession,
    ChatSessionInDB, ChatMessageModel
)
from app.dependencies.auth import get_current_user, get_current_user_optional
from app.models.user import User

current_dir = os.getcwd()
print("Current Directory:", current_dir)

pipeline = Pipeline()
ingestor = Ingestor()

router = APIRouter()


# -------------------------
# Chat Session Endpoints
# -------------------------

@router.post("/chat/sessions", response_model=ChatSession, tags=["Chat Sessions"])
async def create_chat_session(
        session_data: ChatSessionCreate,
        current_user: User = Depends(get_current_user)
):
    """Create a new chat session"""
    session_in_db = ChatSessionInDB(
        **session_data.dict(),
        user_id=current_user.id
    )
    created_session = await chat_repository.create_session(session_in_db)

    return ChatSession(
        _id=str(created_session.id),
        title=created_session.title,
        messages=created_session.messages,
        created_at=created_session.created_at,
        updated_at=created_session.updated_at
    )


@router.get("/chat/sessions", response_model=List[ChatSession], tags=["Chat Sessions"])
async def get_chat_sessions(
        skip: int = 0,
        limit: int = 50,
        current_user: User = Depends(get_current_user)
):
    """Get all chat sessions for the current user"""
    sessions = await chat_repository.get_user_sessions(current_user.id, skip, limit)

    return [
        ChatSession(
            _id=str(session.id),
            title=session.title,
            messages=session.messages,
            created_at=session.created_at,
            updated_at=session.updated_at
        )
        for session in sessions
    ]


@router.get("/chat/sessions/{session_id}", response_model=ChatSession, tags=["Chat Sessions"])
async def get_chat_session(
        session_id: str,
        current_user: User = Depends(get_current_user)
):
    """Get a specific chat session"""
    session = await chat_repository.get_session_by_id(session_id, current_user.id)

    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    return ChatSession(
        _id=str(session.id),
        title=session.title,
        messages=session.messages,
        created_at=session.created_at,
        updated_at=session.updated_at
    )


@router.put("/chat/sessions/{session_id}", response_model=ChatSession, tags=["Chat Sessions"])
async def update_chat_session(
        session_id: str,
        session_update: ChatSessionUpdate,
        current_user: User = Depends(get_current_user)
):
    """Update a chat session (including messages)"""
    updated_session = await chat_repository.update_session(
        session_id,
        current_user.id,
        session_update
    )

    if not updated_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    return ChatSession(
        _id=str(updated_session.id),
        title=updated_session.title,
        messages=updated_session.messages,
        created_at=updated_session.created_at,
        updated_at=updated_session.updated_at
    )


@router.delete("/chat/sessions/{session_id}", tags=["Chat Sessions"])
async def delete_chat_session(
        session_id: str,
        current_user: User = Depends(get_current_user)
):
    """Delete a chat session"""
    deleted = await chat_repository.delete_session(session_id, current_user.id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Chat session not found")

    return {"message": "Chat session deleted successfully"}


# -------------------------
# Chat Endpoints
# -------------------------

class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    query: str
    answer: str


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest):
    dummy_answer = f"This is a dummy response for: '{request.query}'"
    return ChatResponse(query=request.query, answer=dummy_answer)


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            dummy_answer = f"This is a dummy WS response for: '{data}'"
            await websocket.send_text(dummy_answer)
    except WebSocketDisconnect:
        print("Client disconnected from WebSocket")


def fake_stream_generator(query: str, image_data: Optional[bytes] = None):
    response = pipeline.run(query, image_data=image_data)
    tokens = [f"{word} " for word in response.split()]
    for token in tokens:
        yield f"data: {token}\n\n"
        time.sleep(0.05)
    yield "data: [DONE]\n\n"


@router.get("/chat/stream", tags=["Chat"])
async def chat_stream_get(query: str):
    """Stream chat response (GET - for backward compatibility)"""
    print(f'Input of Chat Endpoint (GET): {query}')
    return StreamingResponse(fake_stream_generator(query), media_type="text/event-stream")


@router.post("/chat/stream", tags=["Chat"])
async def chat_stream_post(
        query: str = Form(...),
        image: Optional[UploadFile] = File(None)
):
    """Stream chat response (POST - supports images)"""
    print(f'[POST /chat/stream] Query: {query}')
    print(f'[POST /chat/stream] Image provided: {image is not None}')

    image_data = None
    if image:
        print(f'[POST /chat/stream] Image filename: {image.filename}')
        print(f'[POST /chat/stream] Image content_type: {image.content_type}')
        image_data = await image.read()
        print(f'[POST /chat/stream] Image size: {len(image_data)} bytes')

        if image.content_type and not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    return StreamingResponse(
        fake_stream_generator(query, image_data),
        media_type="text/event-stream"
    )


def run_ingestion_task():
    try:
        result = ingestor.ingest()
    except Exception as e:
        pass


@router.get("/ingest", tags=["Ingest"])
async def ingest_endpoint(background_tasks: BackgroundTasks):
    try:
        print(f'Ingestion request is accepted...')
        background_tasks.add_task(run_ingestion_task)
        return JSONResponse(
            content={"status": "started", "message": "Ingestion has been triggered and is running in the background."},
            status_code=202,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start ingestion: {str(e)}")

