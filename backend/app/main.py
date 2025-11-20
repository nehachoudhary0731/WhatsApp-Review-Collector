from fastapi import FastAPI, Depends, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from datetime import datetime
from pydantic import BaseModel
from .database import get_db_connection
from .models import Review, ReviewCreate, conversation_manager

app = FastAPI(title="WhatsApp Review Collector")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schemas
class ReviewBase(BaseModel):
    contact_number: str
    user_name: str
    product_name: str
    product_review: str

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    created_at: datetime

# Conversation state
conversation_state = {}

@app.get("/")
def read_root():
    return {"message": "WhatsApp Review Collector API"}

@app.get("/api/reviews", response_model=List[Review])
def get_reviews():
    conn = get_db_connection()
    reviews = conn.execute(
        'SELECT id, contact_number, user_name, product_name, product_review, created_at FROM reviews ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    
    return [dict(review) for review in reviews]

@app.post("/api/reviews", response_model=Review)
def create_review(review: ReviewCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO reviews (contact_number, user_name, product_name, product_review) VALUES (?, ?, ?, ?)',
        (review.contact_number, review.user_name, review.product_name, review.product_review)
    )
    
    review_id = cursor.lastrowid
    conn.commit()
    
    # Get the created review
    created_review = conn.execute(
        'SELECT * FROM reviews WHERE id = ?', (review_id,)
    ).fetchone()
    
    conn.close()
    return dict(created_review)

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...)
):
    global conversation_state
    
    message = Body.strip()
    contact_number = From
    
    if contact_number not in conversation_state:
        conversation_state[contact_number] = {
            "step": "initial",
            "product_name": None,
            "user_name": None
        }
    
    state = conversation_state[contact_number]
    response = ""
    
    if state["step"] == "initial":
        if message.lower() in ["hi", "hello", "hey"]:
            response = "Which product is this review for?"
            state["step"] = "awaiting_product"
        else:
            response = "Hello! To start a review, please send 'Hi'"
    
    elif state["step"] == "awaiting_product":
        state["product_name"] = message
        response = "What's your name?"
        state["step"] = "awaiting_name"
    
    elif state["step"] == "awaiting_name":
        state["user_name"] = message
        response = f"Please send your review for {state['product_name']}."
        state["step"] = "awaiting_review"
    
    elif state["step"] == "awaiting_review":
        # Save to database
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO reviews (contact_number, user_name, product_name, product_review) VALUES (?, ?, ?, ?)',
            (contact_number, state["user_name"], state["product_name"], message)
        )
        conn.commit()
        conn.close()
        
        response = f"Thanks {state['user_name']} -- your review for {state['product_name']} has been recorded."
        del conversation_state[contact_number]
    
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response}</Message>
</Response>"""

@app.post("/test/conversation")
def test_conversation_flow(
    contact_number: str = "+1234567890",
    user_name: str = "Test User",
    product_name: str = "Test Product",
    product_review: str = "This is a test review"
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO reviews (contact_number, user_name, product_name, product_review) VALUES (?, ?, ?, ?)',
        (contact_number, user_name, product_name, product_review)
    )
    
    review_id = cursor.lastrowid
    conn.commit()
    
    created_review = conn.execute(
        'SELECT * FROM reviews WHERE id = ?', (review_id,)
    ).fetchone()
    
    conn.close()
    
    return {
        "message": f"Thanks {user_name} -- your review for {product_name} has been recorded.",
        "review": dict(created_review)
    }