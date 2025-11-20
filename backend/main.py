from fastapi import FastAPI, Depends, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import sqlite3
from datetime import datetime
from pydantic import BaseModel

# Pydantic models for request/response validation
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

    class Config:
        from_attributes = True

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('whatsapp_reviews.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_number TEXT NOT NULL,
            user_name TEXT NOT NULL,
            product_name TEXT NOT NULL,
            product_review TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# FastAPI app
app = FastAPI(
    title="WhatsApp Review Collector",
    description="A full-stack application that collects product reviews via WhatsApp messages",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for conversation state (use Redis in production)
conversation_state = {}

@app.get("/")
def read_root():
    """Root endpoint - API information"""
    return {
        "message": "WhatsApp Review Collector API",
        "endpoints": {
            "get_reviews": "GET /api/reviews",
            "create_review": "POST /api/reviews",
            "whatsapp_webhook": "POST /webhook/whatsapp",
            "api_docs": "GET /docs"
        }
    }

@app.get("/api/reviews", response_model=List[Review])
def get_reviews():
    """
    Get all stored reviews in JSON format
    Returns reviews ordered by creation date (newest first)
    """
    conn = get_db_connection()
    reviews = conn.execute(
        'SELECT id, contact_number, user_name, product_name, product_review, created_at FROM reviews ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    
    # Convert to list of dictionaries and handle datetime
    review_list = []
    for review in reviews:
        review_dict = dict(review)
        # Convert string timestamp to datetime object if needed
        if isinstance(review_dict['created_at'], str):
            try:
                review_dict['created_at'] = datetime.fromisoformat(review_dict['created_at'].replace('Z', '+00:00'))
            except:
                # Fallback if datetime conversion fails
                pass
        review_list.append(review_dict)
    
    return review_list

@app.post("/api/reviews", response_model=Review)
def create_review(review: ReviewCreate):
    """
    Create a new review
    Accepts review data in JSON format and stores in database
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO reviews (contact_number, user_name, product_name, product_review) VALUES (?, ?, ?, ?)',
            (review.contact_number, review.user_name, review.product_name, review.product_review)
        )
        
        review_id = cursor.lastrowid
        conn.commit()
        
        # Get the created review with all fields
        created_review = conn.execute(
            'SELECT * FROM reviews WHERE id = ?', (review_id,)
        ).fetchone()
        
        if not created_review:
            raise HTTPException(status_code=500, detail="Failed to create review")
        
        # Convert to dict and handle datetime
        review_dict = dict(created_review)
        if isinstance(review_dict['created_at'], str):
            try:
                review_dict['created_at'] = datetime.fromisoformat(review_dict['created_at'].replace('Z', '+00:00'))
            except:
                pass
        
        return review_dict
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...)
):
    """
    WhatsApp webhook endpoint for Twilio
    Implements the exact conversation flow from the assignment:
    
    User: Hi
    Server: Which product is this review for?
    
    User: [Product Name]
    Server: What's your name?
    
    User: [User Name] 
    Server: Please send your review for [Product Name].
    
    User: [Review Text]
    Server: Thanks [User Name] -- your review for [Product Name] has been recorded.
    """
    global conversation_state
    
    # Clean the message
    message = Body.strip()
    contact_number = From
    
    print(f"📱 WhatsApp message from {contact_number}: {message}")
    
    # Initialize conversation state if not exists
    if contact_number not in conversation_state:
        conversation_state[contact_number] = {
            "step": "initial",
            "product_name": None,
            "user_name": None
        }
    
    state = conversation_state[contact_number]
    response = ""
    
    # Implement exact conversation flow from assignment
    if state["step"] == "initial":
        # User sends greeting
        if message.lower() in ["hi", "hello", "hey"]:
            response = "Which product is this review for?"
            state["step"] = "awaiting_product"
            print(f"🤖 Bot response: {response}")
        else:
            response = "Hello! To start a review, please send 'Hi'"
            print(f"🤖 Bot response: {response}")
    
    elif state["step"] == "awaiting_product":
        # User sends product name
        state["product_name"] = message
        response = "What's your name?"
        state["step"] = "awaiting_name"
        print(f"🤖 Bot response: {response}")
    
    elif state["step"] == "awaiting_name":
        # User sends their name
        state["user_name"] = message
        response = f"Please send your review for {state['product_name']}."
        state["step"] = "awaiting_review"
        print(f"🤖 Bot response: {response}")
    
    elif state["step"] == "awaiting_review":
        # User sends review - save to database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                'INSERT INTO reviews (contact_number, user_name, product_name, product_review) VALUES (?, ?, ?, ?)',
                (contact_number, state["user_name"], state["product_name"], message)
            )
            conn.commit()
            conn.close()
            
            # Exact response format from assignment
            response = f"Thanks {state['user_name']} -- your review for {state['product_name']} has been recorded."
            print(f"✅ Review saved! Bot response: {response}")
            
            # Clear conversation state
            del conversation_state[contact_number]
            print(f"🗑️ Cleared conversation state for {contact_number}")
            
        except Exception as e:
            response = "Sorry, there was an error saving your review. Please try again."
            print(f"❌ Error saving review: {str(e)}")
    
    # Return TwiML response for Twilio
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response}</Message>
</Response>"""

@app.post("/test/conversation")
def test_conversation_flow(
    contact_number: str = "+1234567890",
    user_name: str = "Test User",
    product_name: str = "Test Product",
    product_review: str = "This is a test review from the test endpoint"
):
    """
    Test endpoint to simulate the complete WhatsApp conversation flow
    Useful for testing without actual WhatsApp integration
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO reviews (contact_number, user_name, product_name, product_review) VALUES (?, ?, ?, ?)',
            (contact_number, user_name, product_name, product_review)
        )
        
        review_id = cursor.lastrowid
        conn.commit()
        
        # Get the created review
        created_review = conn.execute(
            'SELECT * FROM reviews WHERE id = ?', (review_id,)
        ).fetchone()
        
        conn.close()
        
        if not created_review:
            raise HTTPException(status_code=500, detail="Failed to create test review")
        
        # Convert to dict
        review_dict = dict(created_review)
        if isinstance(review_dict['created_at'], str):
            try:
                review_dict['created_at'] = datetime.fromisoformat(review_dict['created_at'].replace('Z', '+00:00'))
            except:
                pass
        
        return {
            "message": f"Thanks {user_name} -- your review for {product_name} has been recorded.",
            "review": review_dict
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test error: {str(e)}")

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)