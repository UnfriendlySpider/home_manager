"""
Maintenance management models
Handles home maintenance schedules, history, and service providers
"""

from datetime import datetime, date
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel

class MaintenanceItem(BaseModel):
    """Model for tracking home maintenance items and schedules"""
    
    __tablename__ = "maintenance_items"
    
    # Basic information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # HVAC, Plumbing, etc.
    location = Column(String(100), nullable=True)  # Basement, Roof, etc.
    
    # Scheduling information
    frequency = Column(String(20), nullable=True)  # monthly, quarterly, yearly, etc.
    frequency_months = Column(Integer, nullable=True)  # Custom frequency in months
    next_due_date = Column(Date, nullable=True)
    last_completed_date = Column(Date, nullable=True)
    
    # Priority and status
    priority = Column(String(20), default="medium", nullable=False)  # low, medium, high, urgent
    status = Column(String(20), default="pending", nullable=False)  # pending, in_progress, completed, cancelled
    is_recurring = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Cost information
    estimated_cost = Column(Numeric(10, 2), nullable=True)
    actual_cost = Column(Numeric(10, 2), nullable=True)
    budget_alert_threshold = Column(Numeric(10, 2), nullable=True)
    
    # Service provider information
    preferred_provider = Column(String(200), nullable=True)
    provider_contact = Column(String(500), nullable=True)  # JSON string with contact details
    
    # Additional information
    warranty_expiry = Column(Date, nullable=True)
    manual_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    
    # User tracking
    created_by = Column(String, nullable=False)
    assigned_to = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<MaintenanceItem(id={self.id}, name='{self.name}', category='{self.category}')>"
    
    def is_overdue(self) -> bool:
        """Check if maintenance item is overdue"""
        if self.next_due_date is None:
            return False
        return date.today() > self.next_due_date
    
    def days_until_due(self) -> int:
        """Calculate days until next due date"""
        if self.next_due_date is None:
            return 999999
        delta = self.next_due_date - date.today()
        return delta.days
    
    def calculate_next_due_date(self):
        """Calculate next due date based on frequency"""
        if not self.is_recurring or self.frequency_months is None:
            return
        
        from dateutil.relativedelta import relativedelta
        
        base_date = self.last_completed_date or date.today()
        self.next_due_date = base_date + relativedelta(months=self.frequency_months)
    
    def mark_completed(self, completion_date: date = None, actual_cost: float = None):
        """Mark maintenance item as completed"""
        self.status = "completed"
        self.last_completed_date = completion_date or date.today()
        
        if actual_cost is not None:
            self.actual_cost = actual_cost
        
        # Calculate next due date if recurring
        if self.is_recurring:
            self.calculate_next_due_date()
            self.status = "pending"  # Reset status for next occurrence
        
        self.updated_at = datetime.utcnow()
    
    def get_frequency_display(self) -> str:
        """Get human-readable frequency description"""
        if not self.is_recurring:
            return "One-time"
        
        if self.frequency:
            return self.frequency.title()
        
        if self.frequency_months:
            if self.frequency_months == 1:
                return "Monthly"
            elif self.frequency_months == 3:
                return "Quarterly"
            elif self.frequency_months == 6:
                return "Semi-annually"
            elif self.frequency_months == 12:
                return "Annually"
            else:
                return f"Every {self.frequency_months} months"
        
        return "Custom"

class MaintenanceHistory(BaseModel):
    """Model for tracking maintenance history and records"""
    
    __tablename__ = "maintenance_history"
    
    maintenance_item_id = Column(Integer, ForeignKey("maintenance_items.id"), nullable=False)
    
    # Completion details
    completion_date = Column(Date, nullable=False)
    actual_cost = Column(Numeric(10, 2), nullable=True)
    duration_hours = Column(Numeric(5, 2), nullable=True)
    
    # Service details
    service_provider = Column(String(200), nullable=True)
    technician_name = Column(String(100), nullable=True)
    invoice_number = Column(String(100), nullable=True)
    
    # Work details
    work_performed = Column(Text, nullable=True)
    parts_used = Column(Text, nullable=True)  # JSON string with parts information
    issues_found = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    
    # Quality and satisfaction
    quality_rating = Column(Integer, nullable=True)  # 1-5 scale
    satisfaction_rating = Column(Integer, nullable=True)  # 1-5 scale
    would_recommend = Column(Boolean, nullable=True)
    
    # Documentation
    photos = Column(Text, nullable=True)  # JSON string with photo URLs
    documents = Column(Text, nullable=True)  # JSON string with document URLs
    receipt_url = Column(String(500), nullable=True)
    
    # Notes and follow-up
    notes = Column(Text, nullable=True)
    follow_up_required = Column(Boolean, default=False, nullable=False)
    follow_up_date = Column(Date, nullable=True)
    follow_up_notes = Column(Text, nullable=True)
    
    # User tracking
    completed_by = Column(String, nullable=False)
    
    # Relationships
    maintenance_item = relationship("MaintenanceItem", backref="history_records")
    
    def __repr__(self):
        return f"<MaintenanceHistory(id={self.id}, item_id={self.maintenance_item_id}, date={self.completion_date})>"

class ServiceProvider(BaseModel):
    """Model for managing service providers and contractors"""
    
    __tablename__ = "service_providers"
    
    # Basic information
    name = Column(String(200), nullable=False)
    business_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    
    # Contact information
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    
    # Address information
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(20), nullable=True)
    
    # Service information
    specialties = Column(Text, nullable=True)  # JSON string with service categories
    service_area = Column(String(200), nullable=True)
    hourly_rate = Column(Numeric(8, 2), nullable=True)
    minimum_charge = Column(Numeric(8, 2), nullable=True)
    
    # Business details
    license_number = Column(String(100), nullable=True)
    insurance_info = Column(Text, nullable=True)
    bonded = Column(Boolean, default=False, nullable=False)
    years_in_business = Column(Integer, nullable=True)
    
    # Ratings and reviews
    overall_rating = Column(Numeric(3, 2), nullable=True)  # 0.00 - 5.00
    total_reviews = Column(Integer, default=0, nullable=False)
    
    # Status and preferences
    is_preferred = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_used_date = Column(Date, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<ServiceProvider(id={self.id}, name='{self.name}')>"
    
    def calculate_rating(self):
        """Calculate overall rating from maintenance history"""
        # This would query maintenance history to calculate average rating
        # Implementation would depend on how ratings are stored
        pass
    
    def get_contact_info(self) -> dict:
        """Get formatted contact information"""
        return {
            "name": self.name,
            "business_name": self.business_name,
            "phone": self.phone,
            "email": self.email,
            "website": self.website,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code
        }
