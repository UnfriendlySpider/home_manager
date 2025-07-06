"""
Task management models
Handles household tasks, assignments, and progress tracking
"""

from datetime import datetime, date
from sqlalchemy import Column, String, Text, Boolean, Date, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum

class TaskStatus(enum.Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(enum.Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskCategory(enum.Enum):
    """Task category enumeration"""
    CLEANING = "cleaning"
    MAINTENANCE = "maintenance"
    SHOPPING = "shopping"
    ORGANIZING = "organizing"
    GARDENING = "gardening"
    ADMIN = "admin"
    OTHER = "other"

class Task(BaseModel):
    """Model for tracking household tasks"""
    
    __tablename__ = "tasks"
    
    # Basic information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(TaskCategory), nullable=False, default=TaskCategory.OTHER)
    priority = Column(Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    
    # Assignment and ownership
    assigned_to = Column(String(100), nullable=True)  # Family member name
    created_by = Column(String(100), nullable=False)
    
    # Dates and scheduling
    due_date = Column(Date, nullable=True)
    start_date = Column(Date, nullable=True)
    completed_date = Column(DateTime, nullable=True)
    estimated_hours = Column(Integer, nullable=True)  # Estimated time in hours
    
    # Recurrence
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50), nullable=True)  # daily, weekly, monthly, yearly
    recurrence_interval = Column(Integer, default=1)  # every X days/weeks/months
    
    # Additional fields
    location = Column(String(100), nullable=True)  # Where the task needs to be done
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<Task(title='{self.title}', status='{self.status.value}', assigned_to='{self.assigned_to}')>"
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if self.due_date and self.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            return date.today() > self.due_date
        return False
    
    @property
    def days_until_due(self) -> int:
        """Get number of days until due date"""
        if self.due_date:
            delta = self.due_date - date.today()
            return delta.days
        return 999  # No due date
    
    @property
    def status_display(self) -> str:
        """Get human-readable status"""
        status_map = {
            TaskStatus.PENDING: "Pending",
            TaskStatus.IN_PROGRESS: "In Progress",
            TaskStatus.COMPLETED: "Completed",
            TaskStatus.CANCELLED: "Cancelled"
        }
        return status_map.get(self.status, self.status.value)
    
    @property
    def priority_display(self) -> str:
        """Get human-readable priority"""
        priority_map = {
            TaskPriority.LOW: "Low",
            TaskPriority.MEDIUM: "Medium", 
            TaskPriority.HIGH: "High",
            TaskPriority.URGENT: "Urgent"
        }
        return priority_map.get(self.priority, self.priority.value)
    
    @property
    def category_display(self) -> str:
        """Get human-readable category"""
        category_map = {
            TaskCategory.CLEANING: "Cleaning",
            TaskCategory.MAINTENANCE: "Maintenance",
            TaskCategory.SHOPPING: "Shopping",
            TaskCategory.ORGANIZING: "Organizing",
            TaskCategory.GARDENING: "Gardening",
            TaskCategory.ADMIN: "Administrative",
            TaskCategory.OTHER: "Other"
        }
        return category_map.get(self.category, self.category.value)
    
    def mark_completed(self, completed_by: str = None):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_date = datetime.now()
        if completed_by:
            self.notes = f"{self.notes or ''}\nCompleted by: {completed_by}".strip()
    
    def mark_in_progress(self):
        """Mark task as in progress"""
        self.status = TaskStatus.IN_PROGRESS
        if not self.start_date:
            self.start_date = date.today()

class TaskComment(BaseModel):
    """Model for task comments and updates"""
    
    __tablename__ = "task_comments"
    
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    comment = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)
    
    # Relationship
    task = relationship("Task", backref="comments")
    
    def __repr__(self):
        return f"<TaskComment(task_id={self.task_id}, author='{self.author}')>"
