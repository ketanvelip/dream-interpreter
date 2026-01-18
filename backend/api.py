from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

from database import get_db, init_db, Dream, ChatMessage
from dream_analyzer import DreamAnalyzer

load_dotenv()

app = FastAPI(title="Dream Interpreter API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = DreamAnalyzer()

class DreamCreate(BaseModel):
    user_id: str
    title: str
    description: str
    emotions: Optional[List[str]] = []

class DreamResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: str
    emotions: List[str]
    interpretation: Optional[str]
    symbols: Optional[List[dict]]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    dream_id: int
    message: str

class ChatMessageResponse(BaseModel):
    id: int
    dream_id: int
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def read_root():
    return {
        "message": "Dream Interpreter API",
        "version": "1.0.0",
        "endpoints": {
            "POST /dreams": "Create and analyze a new dream",
            "GET /dreams/{user_id}": "Get all dreams for a user",
            "GET /dreams/{user_id}/{dream_id}": "Get a specific dream",
            "GET /dreams/{user_id}/patterns": "Analyze patterns across user's dreams",
            "POST /dreams/{dream_id}/chat": "Ask follow-up questions about a dream",
            "GET /dreams/{dream_id}/chat": "Get chat history for a dream",
            "DELETE /dreams/{dream_id}": "Delete a dream"
        }
    }

@app.post("/dreams", response_model=DreamResponse)
def create_dream(dream: DreamCreate, db: Session = Depends(get_db)):
    analysis = analyzer.analyze_dream(
        dream_description=dream.description,
        emotions=dream.emotions
    )
    
    db_dream = Dream(
        user_id=dream.user_id,
        title=dream.title,
        description=dream.description,
        emotions=dream.emotions,
        interpretation=analysis["interpretation"],
        symbols=analysis["symbols"]
    )
    
    db.add(db_dream)
    db.commit()
    db.refresh(db_dream)
    
    return db_dream

@app.get("/dreams/{user_id}", response_model=List[DreamResponse])
def get_user_dreams(user_id: str, db: Session = Depends(get_db)):
    dreams = db.query(Dream).filter(Dream.user_id == user_id).order_by(Dream.created_at.desc()).all()
    return dreams

@app.get("/dreams/{user_id}/patterns")
def get_dream_patterns(user_id: str, db: Session = Depends(get_db)):
    dreams = db.query(Dream).filter(Dream.user_id == user_id).order_by(Dream.created_at.desc()).all()
    
    if len(dreams) < 2:
        return {
            "message": "Need at least 2 dreams to identify patterns",
            "dreams_count": len(dreams)
        }
    
    dream_data = [
        {
            "description": d.description,
            "emotions": d.emotions,
            "symbols": d.symbols,
            "created_at": d.created_at.isoformat()
        }
        for d in dreams
    ]
    
    patterns = analyzer.find_patterns(dream_data)
    return patterns

@app.post("/dreams/{dream_id}/chat")
def chat_about_dream(dream_id: int, chat_request: ChatRequest, db: Session = Depends(get_db)):
    dream = db.query(Dream).filter(Dream.id == dream_id).first()
    if not dream:
        raise HTTPException(status_code=404, detail="Dream not found")
    
    chat_history = db.query(ChatMessage).filter(ChatMessage.dream_id == dream_id).order_by(ChatMessage.created_at).all()
    
    history_for_ai = [
        {"role": msg.role, "content": msg.content}
        for msg in chat_history
    ]
    
    dream_context = {
        "title": dream.title,
        "description": dream.description,
        "emotions": dream.emotions or [],
        "interpretation": dream.interpretation
    }
    
    ai_response = analyzer.chat_about_dream(
        dream_context=dream_context,
        chat_history=history_for_ai,
        user_question=chat_request.message
    )
    
    user_message = ChatMessage(
        dream_id=dream_id,
        role="user",
        content=chat_request.message
    )
    db.add(user_message)
    
    assistant_message = ChatMessage(
        dream_id=dream_id,
        role="assistant",
        content=ai_response
    )
    db.add(assistant_message)
    
    db.commit()
    db.refresh(assistant_message)
    
    return assistant_message

@app.get("/dreams/{dream_id}/chat", response_model=List[ChatMessageResponse])
def get_chat_history(dream_id: int, db: Session = Depends(get_db)):
    dream = db.query(Dream).filter(Dream.id == dream_id).first()
    if not dream:
        raise HTTPException(status_code=404, detail="Dream not found")
    
    messages = db.query(ChatMessage).filter(ChatMessage.dream_id == dream_id).order_by(ChatMessage.created_at).all()
    return messages

@app.delete("/dreams/{dream_id}")
def delete_dream(dream_id: int, db: Session = Depends(get_db)):
    dream = db.query(Dream).filter(Dream.id == dream_id).first()
    if not dream:
        raise HTTPException(status_code=404, detail="Dream not found")
    
    db.delete(dream)
    db.commit()
    return {"message": "Dream deleted successfully"}

@app.get("/dreams/{user_id}/{dream_id}", response_model=DreamResponse)
def get_dream(user_id: str, dream_id: int, db: Session = Depends(get_db)):
    dream = db.query(Dream).filter(Dream.id == dream_id, Dream.user_id == user_id).first()
    if not dream:
        raise HTTPException(status_code=404, detail="Dream not found")
    return dream

@app.get("/health")
def health_check():
    return {"status": "healthy"}
