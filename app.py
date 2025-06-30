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

# Import modules (will be created)
# from modules.dashboard.ui import dashboard_ui
# from modules.dashboard.server import dashboard_server

def create_sample_data():
    """Create sample data for demonstration"""
    try:
        db = next(get_database())
        
        # Check if we already have data
        existing_items = db.query(MaintenanceItem).first()
        if existing_items:
            return  # Data already exists
        
        # Create sample maintenance items
        sample_items = [
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
        
        for item in sample_items:
            db.add(item)
        
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
                ui.nav_panel(
                    ui.navset_pill_list(
                        ui.nav_panel("Dashboard", "dashboard"),
                        ui.nav_panel("Maintenance", "maintenance"),
                        ui.nav_panel("Inventory", "inventory"),
                        ui.nav_panel("Financial", "financial"),
                        ui.nav_panel("Tasks", "tasks"),
                        ui.nav_panel("Documents", "documents"),
                        ui.nav_panel("Analytics", "analytics"),
                        ui.nav_panel("Settings", "settings"),
                        id="main_nav"
                    )
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
    
    # Navigation handler
    @reactive.Effect
    @reactive.event(input.main_nav)
    def _handle_navigation():
        current_page.set(input.main_nav())
    
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
            ui.p("Task management features will be implemented here."),
            ui.div(
                {"class": "alert alert-info"},
                "This module is under development. Features will include task assignment, progress tracking, and family coordination."
            )
        )
    
    def render_documents():
        """Render document management page"""
        return ui.div(
            h2("📄 Document Management"),
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
            ui.p("Application settings will be implemented here."),
            ui.div(
                {"class": "alert alert-info"},
                "This module is under development. Features will include user preferences, system configuration, and backup management."
            )
        )

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
