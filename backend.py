from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Import our AI tool
from tool import analyze_complaint

DB_URL = "sqlite:///complaints.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ComplaintModel(Base):
    __tablename__ = "complaints"
    id = Column(Integer, primary_key=True, index=True)
    raw_text = Column(Text, nullable=False)
    category = Column(String, default="General")
    priority = Column(String, default="Medium")
    sentiment = Column(String, default="Neutral")
    summary = Column(Text)
    status = Column(String, default="Open")
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Complaint Prioritization API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ComplaintCreate(BaseModel):
    text: str

@app.post("/complaints/")
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    # 1. Run through AI Tool
    ai_data = analyze_complaint(payload.text)
    
    # 2. Save to Database
    db_item = ComplaintModel(
        raw_text=payload.text,
        category=ai_data.get("category"),
        priority=ai_data.get("priority"),
        sentiment=ai_data.get("sentiment"),
        summary=ai_data.get("summary")
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/complaints/")
def list_complaints(db: Session = Depends(get_db)):
    return db.query(ComplaintModel).order_by(ComplaintModel.created_at.desc()).all()

@app.patch("/complaints/{complaint_id}/resolve")
def resolve_complaint(complaint_id: int, db: Session = Depends(get_db)):
    item = db.query(ComplaintModel).filter(ComplaintModel.id == complaint_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Complaint not found")
    item.status = "Resolved"
    db.commit()
    return {"message": f"Complaint {complaint_id} marked as resolved."}