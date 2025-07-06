"""
Home Manager - Main Application Entry Point
Python Shiny web application for comprehensive home management
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from shiny import App, ui, render, reactive
from htmltools import div, h1, h2, h3, p, tags
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

# Import configuration and database
from config.settings import settings, constants
from config.database import init_database, get_database, check_database_health
from config.auth import session_manager, auth_manager

# Import models
from models.user import User
from models.maintenance import MaintenanceItem
from models.task import Task, TaskComment, TaskStatus, TaskPriority, TaskCategory

# Import modules (will be created)
# from modules.dashboard.ui import dashboard_ui
# from modules.dashboard.server import dashboard_server

def create_sample_data():
    """Create sample data for demonstration"""
    try:
        db = next(get_database())
        
        # Check if we already have maintenance data
        existing_maintenance = db.query(MaintenanceItem).first()
        if not existing_maintenance:
            # Create sample maintenance items
            sample_maintenance = [
                MaintenanceItem(
                    name="HVAC Filter Replacement",
                    description="Replace air filter in main HVAC system",
                    category="HVAC",
                    location="Basement",
                    frequency="monthly",
                    frequency_months=1,
                    next_due_date=date.today() + timedelta(days=15),
                    priority="medium",
                    estimated_cost=25.00,
                    created_by="1"
                ),
                MaintenanceItem(
                    name="Gutter Cleaning",
                    description="Clean gutters and downspouts",
                    category="Exterior",
                    location="Roof",
                    frequency="quarterly",
                    frequency_months=6,
                    next_due_date=date.today() + timedelta(days=45),
                    priority="high",
                    estimated_cost=150.00,
                    created_by="1"
                ),
                MaintenanceItem(
                    name="Water Heater Inspection",
                    description="Annual water heater maintenance and inspection",
                    category="Plumbing",
                    location="Basement",
                    frequency="yearly",
                    frequency_months=12,
                    next_due_date=date.today() + timedelta(days=90),
                    priority="medium",
                    estimated_cost=120.00,
                    created_by="1"
                )
            ]
            
            for item in sample_maintenance:
                db.add(item)
        
        # Check if we already have task data
        existing_tasks = db.query(Task).first()
        if not existing_tasks:
            # Create sample tasks
            sample_tasks = [
                Task(
                    title="Clean Kitchen",
                    description="Deep clean kitchen including appliances and counters",
                    category=TaskCategory.CLEANING,
                    priority=TaskPriority.HIGH,
                    assigned_to="Mom",
                    created_by="Admin",
                    due_date=date.today() + timedelta(days=2),
                    location="Kitchen"
                ),
                Task(
                    title="Fix Leaky Faucet", 
                    description="Repair the bathroom faucet that's been dripping",
                    category=TaskCategory.MAINTENANCE,
                    priority=TaskPriority.MEDIUM,
                    assigned_to="Dad",
                    created_by="Admin",
                    due_date=date.today() + timedelta(days=5),
                    location="Bathroom"
                ),
                Task(
                    title="Grocery Shopping",
                    description="Weekly grocery shopping - check list on fridge",
                    category=TaskCategory.SHOPPING,
                    priority=TaskPriority.MEDIUM,
                    assigned_to="Mom",
                    created_by="Admin",
                    due_date=date.today() + timedelta(days=1),
                    location="Grocery Store"
                ),
                Task(
                    title="Organize Garage",
                    description="Sort and organize items in garage, donate unused items",
                    category=TaskCategory.ORGANIZING,
                    priority=TaskPriority.LOW,
                    assigned_to="Dad",
                    created_by="Admin",
                    due_date=date.today() + timedelta(days=14),
                    location="Garage"
                ),
                Task(
                    title="Water Plants",
                    description="Water all indoor and outdoor plants",
                    category=TaskCategory.GARDENING,
                    priority=TaskPriority.HIGH,
                    assigned_to="Kid1",
                    created_by="Admin",
                    due_date=date.today(),
                    location="House & Garden"
                ),
                Task(
                    title="Vacuum Living Room",
                    description="Vacuum and tidy up the living room",
                    category=TaskCategory.CLEANING,
                    priority=TaskPriority.MEDIUM,
                    status=TaskStatus.COMPLETED,
                    assigned_to="Kid2",
                    created_by="Admin",
                    due_date=date.today() - timedelta(days=1),
                    completed_date=datetime.now() - timedelta(days=1),
                    location="Living Room"
                )
            ]
            
            for task in sample_tasks:
                db.add(task)
        
        db.commit()
        print("Sample data created successfully")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
    finally:
        db.close()

# Main UI Layout
app_ui = ui.page_fluid(
    # Custom CSS
    tags.head(
        tags.link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"),
        tags.script("""
            // Task management client-side functionality
            document.addEventListener('DOMContentLoaded', function() {
                // Add hover effects to task cards
                const taskCards = document.querySelectorAll('.task-card');
                taskCards.forEach(card => {
                    card.addEventListener('mouseenter', function() {
                        this.style.transform = 'translateY(-2px)';
                        this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
                    });
                    card.addEventListener('mouseleave', function() {
                        this.style.transform = 'translateY(0)';
                        this.style.boxShadow = '';
                    });
                });
                
                // Auto-refresh task list every 30 seconds
                setInterval(function() {
                    const refreshBtn = document.getElementById('refresh_tasks');
                    if (refreshBtn) {
                        refreshBtn.click();
                    }
                }, 30000);
            });
        """),
        tags.style("""
            .sidebar {
                background-color: #f8f9fa;
                min-height: 100vh;
                padding: 20px;
            }
            .main-content {
                padding: 20px;
            }
            .metric-card {
                background: linear-gradient(45deg, #007bff, #0056b3);
                color: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .metric-number {
                font-size: 2.5rem;
                font-weight: bold;
            }
            .metric-label {
                font-size: 0.9rem;
                opacity: 0.9;
            }
            .status-overdue { color: #dc3545; font-weight: bold; }
            .status-due-soon { color: #ffc107; font-weight: bold; }
            .status-upcoming { color: #28a745; }
            .card-header {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                font-weight: bold;
            }
            .nav-button:hover {
                background-color: #0056b3 !important;
                color: white !important;
            }
            .nav-button.active {
                background-color: #007bff !important;
                color: white !important;
                border-color: #007bff !important;
            }
            .task-card {
                transition: all 0.3s ease;
            }
            .task-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .task-priority-urgent {
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.7; }
                100% { opacity: 1; }
            }
            .task-overdue {
                border-left: 4px solid #dc3545;
                background-color: #fff5f5;
            }
            .task-due-soon {
                border-left: 4px solid #ffc107;
                background-color: #fffbf0;
            }
            .task-completed {
                opacity: 0.8;
                background-color: #f8f9fa;
            }
            .badge-category {
                font-size: 0.75rem;
                padding: 0.25rem 0.5rem;
            }
        """)
    ),
    
    # Navigation Header
    ui.div(
        {"class": "container-fluid bg-primary text-white py-3 mb-4"},
        ui.div(
            {"class": "row"},
            ui.div(
                {"class": "col"},
                h1("🏠 Home Manager", {"class": "mb-0"}),
                p("Comprehensive Home Management System", {"class": "mb-0 opacity-75"})
            ),
            ui.div(
                {"class": "col-auto"},
                ui.span(f"Version {settings.APP_VERSION}", {"class": "badge bg-light text-dark"})
            )
        )
    ),
    
    # Main Layout
    ui.div(
        {"class": "container-fluid"},
        ui.div(
            {"class": "row"},
            # Sidebar
            ui.div(
                {"class": "col-md-3 col-lg-2 sidebar"},
                h3("Navigation"),
                ui.div(
                    {"class": "nav flex-column"},
                    ui.input_action_button("nav_dashboard", "📊 Dashboard", 
                                          class_="btn btn-outline-primary w-100 mb-2 text-start nav-button"),
                    ui.input_action_button("nav_maintenance", "🔧 Maintenance", 
                                          class_="btn btn-outline-primary w-100 mb-2 text-start nav-button"),
                    ui.input_action_button("nav_inventory", "📦 Inventory", 
                                          class_="btn btn-outline-primary w-100 mb-2 text-start nav-button"),
                    ui.input_action_button("nav_financial", "💰 Financial", 
                                          class_="btn btn-outline-primary w-100 mb-2 text-start nav-button"),
                    ui.input_action_button("nav_tasks", "✅ Tasks", 
                                          class_="btn btn-outline-primary w-100 mb-2 text-start nav-button"),
                    ui.input_action_button("nav_documents", "📄 Documents", 
                                          class_="btn btn-outline-primary w-100 mb-2 text-start nav-button"),
                    ui.input_action_button("nav_analytics", "📈 Analytics", 
                                          class_="btn btn-outline-primary w-100 mb-2 text-start nav-button"),
                    ui.input_action_button("nav_settings", "⚙️ Settings", 
                                          class_="btn btn-outline-primary w-100 mb-2 text-start nav-button")
                )
            ),
            
            # Main Content Area
            ui.div(
                {"class": "col-md-9 col-lg-10 main-content"},
                
                # Dashboard Content
                ui.output_ui("main_content")
            )
        )
    )
)

def server(input, output, session):
    """Main server function"""
    
    # Reactive values for application state
    current_user = reactive.Value(None)
    current_page = reactive.Value("dashboard")
    
    # Initialize database and create sample data
    @reactive.Effect
    def _init_app():
        try:
            init_database()
            create_sample_data()
        except Exception as e:
            print(f"Error initializing app: {e}")
    
    # Navigation handlers
    @reactive.Effect
    @reactive.event(input.nav_dashboard)
    def _handle_dashboard():
        current_page.set("dashboard")
    
    @reactive.Effect
    @reactive.event(input.nav_maintenance)
    def _handle_maintenance():
        current_page.set("maintenance")
    
    @reactive.Effect
    @reactive.event(input.nav_inventory)
    def _handle_inventory():
        current_page.set("inventory")
    
    @reactive.Effect
    @reactive.event(input.nav_financial)
    def _handle_financial():
        current_page.set("financial")
    
    @reactive.Effect
    @reactive.event(input.nav_tasks)
    def _handle_tasks():
        current_page.set("tasks")
    
    @reactive.Effect
    @reactive.event(input.nav_documents)
    def _handle_documents():
        current_page.set("documents")
    
    @reactive.Effect
    @reactive.event(input.nav_analytics)
    def _handle_analytics():
        current_page.set("analytics")
    
    @reactive.Effect
    @reactive.event(input.nav_settings)
    def _handle_settings():
        current_page.set("settings")
    
    # Main content renderer
    @output
    @render.ui
    def main_content():
        page = current_page.get()
        
        if page == "dashboard":
            return render_dashboard()
        elif page == "maintenance":
            return render_maintenance()
        elif page == "inventory":
            return render_inventory()
        elif page == "financial":
            return render_financial()
        elif page == "tasks":
            return render_tasks()
        elif page == "documents":
            return render_documents()
        elif page == "analytics":
            return render_analytics()
        elif page == "settings":
            return render_settings()
        else:
            return render_dashboard()  # Default to dashboard
    
    def render_dashboard():
        """Render the main dashboard"""
        try:
            # Get maintenance data
            db = next(get_database())
            maintenance_items = db.query(MaintenanceItem).filter(MaintenanceItem.is_active == True).all()
            
            # Calculate metrics
            total_items = len(maintenance_items)
            overdue_items = len([item for item in maintenance_items if item.is_overdue()])
            due_soon_items = len([item for item in maintenance_items if 0 <= item.days_until_due() <= 7 and not item.is_overdue()])
            completed_this_month = len([item for item in maintenance_items if item.last_completed_date and item.last_completed_date.month == date.today().month])
            
            # Create charts data
            if maintenance_items:
                # Category distribution
                category_counts = {}
                for item in maintenance_items:
                    category_counts[item.category] = category_counts.get(item.category, 0) + 1
                
                # Priority distribution
                priority_counts = {}
                for item in maintenance_items:
                    priority_counts[item.priority] = priority_counts.get(item.priority, 0) + 1
            else:
                category_counts = {"No Data": 1}
                priority_counts = {"No Data": 1}
            
            db.close()
            
            return ui.div(
                h2("📊 Dashboard"),
                
                # Metrics Row
                ui.div(
                    {"class": "row mb-4"},
                    ui.div(
                        {"class": "col-md-3"},
                        ui.div(
                            {"class": "metric-card text-center"},
                            ui.div(str(total_items), {"class": "metric-number"}),
                            ui.div("Total Items", {"class": "metric-label"})
                        )
                    ),
                    ui.div(
                        {"class": "col-md-3"},
                        ui.div(
                            {"class": "metric-card text-center", "style": "background: linear-gradient(45deg, #dc3545, #c82333);"},
                            ui.div(str(overdue_items), {"class": "metric-number"}),
                            ui.div("Overdue", {"class": "metric-label"})
                        )
                    ),
                    ui.div(
                        {"class": "col-md-3"},
                        ui.div(
                            {"class": "metric-card text-center", "style": "background: linear-gradient(45deg, #ffc107, #e0a800);"},
                            ui.div(str(due_soon_items), {"class": "metric-number"}),
                            ui.div("Due Soon", {"class": "metric-label"})
                        )
                    ),
                    ui.div(
                        {"class": "col-md-3"},
                        ui.div(
                            {"class": "metric-card text-center", "style": "background: linear-gradient(45deg, #28a745, #1e7e34);"},
                            ui.div(str(completed_this_month), {"class": "metric-number"}),
                            ui.div("Completed This Month", {"class": "metric-label"})
                        )
                    )
                ),
                
                # Charts Row
                ui.div(
                    {"class": "row mb-4"},
                    ui.div(
                        {"class": "col-md-6"},
                        ui.div(
                            {"class": "card"},
                            ui.div({"class": "card-header"}, "Maintenance by Category"),
                            ui.div(
                                {"class": "card-body"},
                                ui.output_plot("category_chart")
                            )
                        )
                    ),
                    ui.div(
                        {"class": "col-md-6"},
                        ui.div(
                            {"class": "card"},
                            ui.div({"class": "card-header"}, "Items by Priority"),
                            ui.div(
                                {"class": "card-body"},
                                ui.output_plot("priority_chart")
                            )
                        )
                    )
                ),
                
                # Recent Activity
                ui.div(
                    {"class": "row"},
                    ui.div(
                        {"class": "col-12"},
                        ui.div(
                            {"class": "card"},
                            ui.div({"class": "card-header"}, "Upcoming Maintenance"),
                            ui.div(
                                {"class": "card-body"},
                                ui.output_ui("upcoming_maintenance")
                            )
                        )
                    )
                )
            )
            
        except Exception as e:
            return ui.div(
                {"class": "alert alert-danger"},
                f"Error loading dashboard: {str(e)}"
            )
    
    @output
    @render.plot
    def category_chart():
        try:
            db = next(get_database())
            maintenance_items = db.query(MaintenanceItem).filter(MaintenanceItem.is_active == True).all()
            db.close()
            
            if not maintenance_items:
                return px.pie(values=[1], names=["No Data"], title="No maintenance items found")
            
            category_counts = {}
            for item in maintenance_items:
                category_counts[item.category] = category_counts.get(item.category, 0) + 1
            
            fig = px.pie(
                values=list(category_counts.values()),
                names=list(category_counts.keys()),
                color_discrete_sequence=settings.CHART_COLOR_PALETTE
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            return fig
        except Exception as e:
            return px.pie(values=[1], names=[f"Error: {str(e)}"])
    
    @output
    @render.plot  
    def priority_chart():
        try:
            db = next(get_database())
            maintenance_items = db.query(MaintenanceItem).filter(MaintenanceItem.is_active == True).all()
            db.close()
            
            if not maintenance_items:
                return px.bar(x=["No Data"], y=[1], title="No maintenance items found")
            
            priority_counts = {}
            for item in maintenance_items:
                priority_counts[item.priority] = priority_counts.get(item.priority, 0) + 1
            
            colors = {
                "low": "#28a745",
                "medium": "#ffc107", 
                "high": "#fd7e14",
                "urgent": "#dc3545"
            }
            
            fig = px.bar(
                x=list(priority_counts.keys()),
                y=list(priority_counts.values()),
                color=list(priority_counts.keys()),
                color_discrete_map=colors
            )
            fig.update_layout(showlegend=False)
            return fig
        except Exception as e:
            return px.bar(x=[f"Error: {str(e)}"], y=[1])
    
    @output
    @render.ui
    def upcoming_maintenance():
        try:
            db = next(get_database())
            maintenance_items = db.query(MaintenanceItem).filter(
                MaintenanceItem.is_active == True,
                MaintenanceItem.next_due_date.isnot(None)
            ).order_by(MaintenanceItem.next_due_date).limit(10).all()
            db.close()
            
            if not maintenance_items:
                return ui.p("No upcoming maintenance scheduled.", {"class": "text-muted"})
            
            items_html = []
            for item in maintenance_items:
                days_until = item.days_until_due()
                
                if item.is_overdue():
                    status_class = "status-overdue"
                    status_text = f"Overdue by {abs(days_until)} days"
                elif days_until <= 7:
                    status_class = "status-due-soon"
                    status_text = f"Due in {days_until} days"
                else:
                    status_class = "status-upcoming"
                    status_text = f"Due in {days_until} days"
                
                items_html.append(
                    ui.div(
                        {"class": "d-flex justify-content-between align-items-center py-2 border-bottom"},
                        ui.div(
                            ui.strong(item.name),
                            ui.br(),
                            ui.small(f"{item.category} - {item.location}", {"class": "text-muted"})
                        ),
                        ui.div(
                            ui.span(status_text, {"class": status_class}),
                            ui.br(),
                            ui.small(f"Due: {item.next_due_date}", {"class": "text-muted"})
                        )
                    )
                )
            
            return ui.div(*items_html)
            
        except Exception as e:
            return ui.div(
                {"class": "alert alert-warning"},
                f"Error loading upcoming maintenance: {str(e)}"
            )
    
    def render_maintenance():
        """Render maintenance management page"""
        return ui.div(
            h2("🔧 Maintenance Management"),
            ui.div(
                {"class": "alert alert-success mb-3"},
                "✅ Navigation working! You are now on the Maintenance page."
            ),
            ui.p("Maintenance management features will be implemented here."),
            ui.div(
                {"class": "alert alert-info"},
                "This module is under development. Features will include maintenance scheduling, service provider management, and cost tracking."
            )
        )
    
    def render_inventory():
        """Render inventory management page"""
        return ui.div(
            h2("📦 Inventory Management"),
            ui.div(
                {"class": "alert alert-success mb-3"},
                "✅ Navigation working! You are now on the Inventory page."
            ),
            ui.p("Inventory management features will be implemented here."),
            ui.div(
                {"class": "alert alert-info"},
                "This module is under development. Features will include item tracking, categorization, and low-stock alerts."
            )
        )
    
    def render_financial():
        """Render financial management page"""
        return ui.div(
            h2("💰 Financial Management"),
            ui.div(
                {"class": "alert alert-success mb-3"},
                "✅ Navigation working! You are now on the Financial page."
            ),
            ui.p("Financial management features will be implemented here."),
            ui.div(
                {"class": "alert alert-info"},
                "This module is under development. Features will include expense tracking, budget management, and financial reporting."
            )
        )
    
    def render_tasks():
        """Render task management page"""
        return ui.div(
            h2("✅ Task Management"),
            
            # Task creation form
            ui.div(
                {"class": "row mb-4"},
                ui.div(
                    {"class": "col-12"},
                    ui.div(
                        {"class": "card"},
                        ui.div({"class": "card-header"}, "📝 Create New Task"),
                        ui.div(
                            {"class": "card-body"},
                            ui.div(
                                {"class": "row"},
                                ui.div(
                                    {"class": "col-md-6"},
                                    ui.input_text("task_title", "Task Title", placeholder="Enter task title..."),
                                    ui.input_select(
                                        "task_category",
                                        "Category",
                                        choices={
                                            "cleaning": "🧹 Cleaning",
                                            "maintenance": "🔧 Maintenance", 
                                            "shopping": "🛒 Shopping",
                                            "organizing": "📦 Organizing",
                                            "gardening": "🌱 Gardening",
                                            "admin": "📋 Administrative",
                                            "other": "📌 Other"
                                        },
                                        selected="other"
                                    ),
                                    ui.input_select(
                                        "task_priority",
                                        "Priority",
                                        choices={
                                            "low": "🔵 Low",
                                            "medium": "🟡 Medium",
                                            "high": "🟠 High", 
                                            "urgent": "🔴 Urgent"
                                        },
                                        selected="medium"
                                    )
                                ),
                                ui.div(
                                    {"class": "col-md-6"},
                                    ui.input_text("task_assigned_to", "Assign To", placeholder="Family member name..."),
                                    ui.input_date("task_due_date", "Due Date"),
                                    ui.input_text("task_location", "Location", placeholder="Where should this be done?")
                                )
                            ),
                            ui.input_text_area("task_description", "Description", placeholder="Task details and instructions..."),
                            ui.div(
                                {"class": "mt-3"},
                                ui.input_action_button("create_task", "Create Task", class_="btn btn-primary"),
                                ui.input_action_button("clear_task_form", "Clear Form", class_="btn btn-secondary ms-2")
                            )
                        )
                    )
                )
            ),
            
            # Task filters and controls
            ui.div(
                {"class": "row mb-4"},
                ui.div(
                    {"class": "col-12"},
                    ui.div(
                        {"class": "card"},
                        ui.div({"class": "card-header"}, "🔍 Filter & View Tasks"),
                        ui.div(
                            {"class": "card-body"},
                            ui.div(
                                {"class": "row"},
                                ui.div(
                                    {"class": "col-md-3"},
                                    ui.input_select(
                                        "filter_status",
                                        "Status",
                                        choices={
                                            "all": "All Tasks",
                                            "pending": "Pending",
                                            "in_progress": "In Progress",
                                            "completed": "Completed",
                                            "overdue": "Overdue"
                                        },
                                        selected="all"
                                    )
                                ),
                                ui.div(
                                    {"class": "col-md-3"},
                                    ui.input_select(
                                        "filter_category",
                                        "Category",
                                        choices={
                                            "all": "All Categories",
                                            "cleaning": "Cleaning",
                                            "maintenance": "Maintenance",
                                            "shopping": "Shopping",
                                            "organizing": "Organizing",
                                            "gardening": "Gardening",
                                            "admin": "Administrative",
                                            "other": "Other"
                                        },
                                        selected="all"
                                    )
                                ),
                                ui.div(
                                    {"class": "col-md-3"},
                                    ui.input_select(
                                        "filter_assigned",
                                        "Assigned To",
                                        choices={"all": "All Members"},
                                        selected="all"
                                    )
                                ),
                                ui.div(
                                    {"class": "col-md-3"},
                                    ui.input_action_button("refresh_tasks", "Refresh", class_="btn btn-outline-primary")
                                )
                            )
                        )
                    )
                )
            ),
            
            # Task statistics
            ui.div(
                {"class": "row mb-4"},
                ui.output_ui("task_stats")
            ),
            
            # Task list
            ui.div(
                {"class": "row"},
                ui.div(
                    {"class": "col-12"},
                    ui.div(
                        {"class": "card"},
                        ui.div({"class": "card-header"}, "📋 Task List"),
                        ui.div(
                            {"class": "card-body"},
                            ui.output_ui("task_list")
                        )
                    )
                )
            )
        )
    
    def render_documents():
        """Render document management page"""
        return ui.div(
            h2("📄 Document Management"),
            ui.div(
                {"class": "alert alert-success mb-3"},
                "✅ Navigation working! You are now on the Documents page."
            ),
            ui.p("Document management features will be implemented here."),
            ui.div(
                {"class": "alert alert-info"},
                "This module is under development. Features will include document storage, organization, and search capabilities."
            )
        )
    
    def render_analytics():
        """Render analytics page"""
        return ui.div(
            h2("📈 Analytics & Reporting"),
            ui.div(
                {"class": "alert alert-success mb-3"},
                "✅ Navigation working! You are now on the Analytics page."
            ),
            ui.p("Analytics and reporting features will be implemented here."),
            ui.div(
                {"class": "alert alert-info"},
                "This module is under development. Features will include advanced analytics, custom reports, and data visualization."
            )
        )
    
    def render_settings():
        """Render settings page"""
        return ui.div(
            h2("⚙️ Settings"),
            ui.div(
                {"class": "alert alert-success mb-3"},
                "✅ Navigation working! You are now on the Settings page."
            ),
            ui.p("Application settings will be implemented here."),
            ui.div(
                {"class": "alert alert-info"},
                "This module is under development. Features will include user preferences, system configuration, and backup management."
            )
        )
    
    # Task Management Server Logic
    
    # Create sample tasks if none exist
    @reactive.Effect
    def _create_sample_tasks():
        try:
            db = next(get_database())
            existing_tasks = db.query(Task).first()
            if not existing_tasks:
                sample_tasks = [
                    Task(
                        title="Clean Kitchen",
                        description="Deep clean kitchen including appliances and counters",
                        category=TaskCategory.CLEANING,
                        priority=TaskPriority.HIGH,
                        assigned_to="Mom",
                        created_by="Admin",
                        due_date=date.today() + timedelta(days=2),
                        location="Kitchen"
                    ),
                    Task(
                        title="Fix Leaky Faucet",
                        description="Repair the bathroom faucet that's been dripping",
                        category=TaskCategory.MAINTENANCE,
                        priority=TaskPriority.MEDIUM,
                        assigned_to="Dad",
                        created_by="Admin",
                        due_date=date.today() + timedelta(days=5),
                        location="Bathroom"
                    ),
                    Task(
                        title="Grocery Shopping",
                        description="Weekly grocery shopping - check list on fridge",
                        category=TaskCategory.SHOPPING,
                        priority=TaskPriority.MEDIUM,
                        assigned_to="Mom",
                        created_by="Admin",
                        due_date=date.today() + timedelta(days=1),
                        location="Grocery Store"
                    ),
                    Task(
                        title="Organize Garage",
                        description="Sort and organize items in garage, donate unused items",
                        category=TaskCategory.ORGANIZING,
                        priority=TaskPriority.LOW,
                        assigned_to="Dad",
                        created_by="Admin",
                        due_date=date.today() + timedelta(days=14),
                        location="Garage"
                    ),
                    Task(
                        title="Water Plants",
                        description="Water all indoor and outdoor plants",
                        category=TaskCategory.GARDENING,
                        priority=TaskPriority.HIGH,
                        assigned_to="Kid1",
                        created_by="Admin",
                        due_date=date.today(),
                        location="House & Garden"
                    )
                ]
                
                for task in sample_tasks:
                    db.add(task)
                db.commit()
            db.close()
        except Exception as e:
            print(f"Error creating sample tasks: {e}")
    
    # Task creation handler
    @reactive.Effect
    @reactive.event(input.create_task)
    def _create_task():
        if not input.task_title() or not input.task_title().strip():
            return
        
        try:
            db = next(get_database())
            new_task = Task(
                title=input.task_title().strip(),
                description=input.task_description() or None,
                category=TaskCategory(input.task_category()),
                priority=TaskPriority(input.task_priority()),
                assigned_to=input.task_assigned_to() or None,
                created_by="Current User",  # Would be actual user in real app
                due_date=input.task_due_date() if input.task_due_date() else None,
                location=input.task_location() or None
            )
            
            db.add(new_task)
            db.commit()
            db.close()
            
            # Clear form after successful creation
            # Note: In a real app, you'd update the inputs programmatically
            
        except Exception as e:
            print(f"Error creating task: {e}")
    
    # Clear form handler
    @reactive.Effect
    @reactive.event(input.clear_task_form)
    def _clear_task_form():
        # In a real Shiny app, you'd reset the input values here
        pass
    
    # Task statistics output
    @output
    @render.ui
    def task_stats():
        try:
            db = next(get_database())
            
            # Get all active tasks
            all_tasks = db.query(Task).filter(Task.is_active == True).all()
            
            # Calculate statistics
            total_tasks = len(all_tasks)
            pending_tasks = len([t for t in all_tasks if t.status == TaskStatus.PENDING])
            in_progress_tasks = len([t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS])
            completed_tasks = len([t for t in all_tasks if t.status == TaskStatus.COMPLETED])
            overdue_tasks = len([t for t in all_tasks if t.is_overdue])
            
            db.close()
            
            return ui.div(
                ui.div(
                    {"class": "col-md-2"},
                    ui.div(
                        {"class": "metric-card text-center", "style": "background: linear-gradient(45deg, #6c757d, #495057);"},
                        ui.div(str(total_tasks), {"class": "metric-number"}),
                        ui.div("Total Tasks", {"class": "metric-label"})
                    )
                ),
                ui.div(
                    {"class": "col-md-2"},
                    ui.div(
                        {"class": "metric-card text-center", "style": "background: linear-gradient(45deg, #ffc107, #e0a800);"},
                        ui.div(str(pending_tasks), {"class": "metric-number"}),
                        ui.div("Pending", {"class": "metric-label"})
                    )
                ),
                ui.div(
                    {"class": "col-md-2"},
                    ui.div(
                        {"class": "metric-card text-center", "style": "background: linear-gradient(45deg, #17a2b8, #138496);"},
                        ui.div(str(in_progress_tasks), {"class": "metric-number"}),
                        ui.div("In Progress", {"class": "metric-label"})
                    )
                ),
                ui.div(
                    {"class": "col-md-2"},
                    ui.div(
                        {"class": "metric-card text-center", "style": "background: linear-gradient(45deg, #28a745, #1e7e34);"},
                        ui.div(str(completed_tasks), {"class": "metric-number"}),
                        ui.div("Completed", {"class": "metric-label"})
                    )
                ),
                ui.div(
                    {"class": "col-md-2"},
                    ui.div(
                        {"class": "metric-card text-center", "style": "background: linear-gradient(45deg, #dc3545, #c82333);"},
                        ui.div(str(overdue_tasks), {"class": "metric-number"}),
                        ui.div("Overdue", {"class": "metric-label"})
                    )
                ),
                ui.div(
                    {"class": "col-md-2"},
                    ui.div(
                        {"class": "metric-card text-center", "style": "background: linear-gradient(45deg, #007bff, #0056b3);"},
                        ui.div(f"{completed_tasks}/{total_tasks}", {"class": "metric-number", "style": "font-size: 1.8rem;"}),
                        ui.div("Completion", {"class": "metric-label"})
                    )
                ),
                class_="row"
            )
            
        except Exception as e:
            return ui.div(
                {"class": "alert alert-warning"},
                f"Error loading task statistics: {str(e)}"
            )
    
    # Task list output
    @output
    @render.ui
    def task_list():
        try:
            db = next(get_database())
            
            # Get filter values
            status_filter = input.filter_status() if hasattr(input, 'filter_status') and input.filter_status() else "all"
            category_filter = input.filter_category() if hasattr(input, 'filter_category') and input.filter_category() else "all"
            
            # Build query
            query = db.query(Task).filter(Task.is_active == True)
            
            # Apply filters
            if status_filter != "all":
                if status_filter == "overdue":
                    # Filter for overdue tasks
                    query = query.filter(
                        Task.due_date < date.today(),
                        Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
                    )
                else:
                    query = query.filter(Task.status == TaskStatus(status_filter))
            
            if category_filter != "all":
                query = query.filter(Task.category == TaskCategory(category_filter))
            
            # Get tasks ordered by priority and due date
            tasks = query.order_by(
                Task.priority.desc(),
                Task.due_date.asc().nullslast()
            ).all()
            
            db.close()
            
            if not tasks:
                return ui.div(
                    {"class": "text-center py-4"},
                    ui.p("No tasks found matching the current filters.", {"class": "text-muted"})
                )
            
            # Build task cards
            task_cards = []
            for task in tasks:
                # Determine status styling
                if task.is_overdue:
                    status_class = "border-danger"
                    status_badge = "badge bg-danger"
                elif task.status == TaskStatus.COMPLETED:
                    status_class = "border-success"
                    status_badge = "badge bg-success"
                elif task.status == TaskStatus.IN_PROGRESS:
                    status_class = "border-info"
                    status_badge = "badge bg-info"
                else:
                    status_class = "border-warning"
                    status_badge = "badge bg-warning text-dark"
                
                # Priority styling
                priority_colors = {
                    TaskPriority.LOW: "text-muted",
                    TaskPriority.MEDIUM: "text-warning",
                    TaskPriority.HIGH: "text-danger",
                    TaskPriority.URGENT: "text-danger fw-bold"
                }
                priority_class = priority_colors.get(task.priority, "text-muted")
                
                # Due date formatting
                due_date_text = ""
                if task.due_date:
                    days_until = task.days_until_due
                    if task.is_overdue:
                        due_date_text = f"Overdue by {abs(days_until)} days"
                        due_date_class = "text-danger"
                    elif days_until == 0:
                        due_date_text = "Due today"
                        due_date_class = "text-warning"
                    elif days_until <= 3:
                        due_date_text = f"Due in {days_until} days"
                        due_date_class = "text-warning"
                    else:
                        due_date_text = f"Due in {days_until} days"
                        due_date_class = "text-muted"
                else:
                    due_date_text = "No due date"
                    due_date_class = "text-muted"
                
                task_card = ui.div(
                    {"class": f"card mb-3 {status_class}"},
                    ui.div(
                        {"class": "card-body"},
                        ui.div(
                            {"class": "d-flex justify-content-between align-items-start"},
                            ui.div(
                                ui.h5(task.title, {"class": "card-title mb-1"}),
                                ui.div(
                                    {"class": "mb-2"},
                                    ui.span(task.status_display, {"class": status_badge}),
                                    " ",
                                    ui.span(task.priority_display, {"class": f"badge bg-light text-dark {priority_class}"}),
                                    " ",
                                    ui.span(task.category_display, {"class": "badge bg-secondary"})
                                )
                            ),
                            ui.div(
                                {"class": "text-end"},
                                ui.small(due_date_text, {"class": due_date_class}),
                                ui.br() if task.assigned_to else "",
                                ui.small(f"👤 {task.assigned_to}", {"class": "text-muted"}) if task.assigned_to else ""
                            )
                        ),
                        ui.p(task.description, {"class": "card-text"}) if task.description else "",
                        ui.div(
                            {"class": "d-flex justify-content-between align-items-center"},
                            ui.div(
                                ui.small(f"📍 {task.location}", {"class": "text-muted"}) if task.location else "",
                                ui.br() if task.location and task.created_date else "",
                                ui.small(f"Created: {task.created_date.strftime('%Y-%m-%d')}", {"class": "text-muted"}) if task.created_date else ""
                            ),
                            ui.div(
                                {"class": "btn-group"},
                                ui.input_action_button(f"task_complete_{task.id}", "✅ Complete", 
                                                      class_="btn btn-sm btn-success") if task.status != TaskStatus.COMPLETED else "",
                                ui.input_action_button(f"task_progress_{task.id}", "⏳ Progress", 
                                                      class_="btn btn-sm btn-info") if task.status == TaskStatus.PENDING else "",
                                ui.input_action_button(f"task_edit_{task.id}", "✏️ Edit", 
                                                      class_="btn btn-sm btn-outline-primary")
                            )
                        )
                    )
                )
                task_cards.append(task_card)
            
            return ui.div(*task_cards)
            
        except Exception as e:
            return ui.div(
                {"class": "alert alert-danger"},
                f"Error loading tasks: {str(e)}"
            )
    
    # Dynamic task action handlers
    # Note: In a production app, you'd want more sophisticated handling for dynamic button IDs
    
    # Update family member choices based on existing assignments
    @reactive.Effect
    def _update_assigned_choices():
        try:
            db = next(get_database())
            # Get unique assigned_to values
            assigned_members = db.query(Task.assigned_to).filter(
                Task.assigned_to.isnot(None),
                Task.is_active == True
            ).distinct().all()
            
            choices = {"all": "All Members"}
            for member_tuple in assigned_members:
                member = member_tuple[0]
                if member:
                    choices[member] = member
            
            # Would update the select input choices here in a real app
            db.close()
            
        except Exception as e:
            print(f"Error updating assigned choices: {e}")
    
    # Sample function to handle task completion
    # In a real app, you'd need to dynamically bind these based on task IDs
    def handle_task_completion(task_id: int):
        """Handle marking a task as completed"""
        try:
            db = next(get_database())
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.mark_completed("Current User")
                db.commit()
            db.close()
        except Exception as e:
            print(f"Error completing task {task_id}: {e}")
    
    def handle_task_progress(task_id: int):
        """Handle marking a task as in progress"""
        try:
            db = next(get_database())
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.mark_in_progress()
                db.commit()
            db.close()
        except Exception as e:
            print(f"Error updating task progress {task_id}: {e}")
    
    # Refresh tasks handler
    @reactive.Effect
    @reactive.event(input.refresh_tasks)
    def _refresh_tasks():
        # Force refresh of reactive outputs
        pass
# Create the Shiny app
app = App(app_ui, server)

if __name__ == "__main__":
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Database: {settings.DATABASE_URL}")
    print(f"Debug mode: {settings.DEBUG}")
    
    # Check database health
    if check_database_health():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
    
    # Run the app
    app.run(host="127.0.0.1", port=8000, debug=settings.DEBUG)
