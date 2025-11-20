"""
Data models for WhatsApp Review Collector
This file defines the data structure using Pydantic for API validation
"""

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

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

class ConversationState:
    """Class to manage conversation state"""
    def __init__(self):
        self.states = {}
    
    def get_state(self, contact_number: str) -> dict:
        """Get conversation state for a contact"""
        if contact_number not in self.states:
            self.states[contact_number] = {
                "step": "initial",
                "product_name": None,
                "user_name": None
            }
        return self.states[contact_number]
    
    def clear_state(self, contact_number: str):
        """Clear conversation state for a contact"""
        if contact_number in self.states:
            del self.states[contact_number]
    
    def update_state(self, contact_number: str, updates: dict):
        """Update conversation state for a contact"""
        if contact_number in self.states:
            self.states[contact_number].update(updates)

# Global conversation state manager
conversation_manager = ConversationState()