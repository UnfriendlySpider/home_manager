# 🏠 Home Manager - Python Shiny Application

A comprehensive home management system built with Python Shiny, designed to help homeowners efficiently manage various aspects of their home including maintenance, inventory, bills, and household tasks.

## 🌟 Features

### Core Modules
- **📊 Dashboard**: Real-time overview with key metrics and visualizations
- **🔧 Maintenance Management**: Schedule and track home maintenance tasks
- **📦 Inventory Management**: Track household items and supplies
- **💰 Financial Management**: Monitor expenses, bills, and budgets
- **✅ Task Management**: Organize and assign household chores
- **📄 Document Management**: Store and organize important documents
- **📈 Analytics & Reporting**: Advanced data analysis and reporting
- **⚙️ Settings**: User preferences and system configuration

### Key Features
- **Reactive Web Interface**: Real-time updates using Python Shiny
- **Multi-user Support**: Role-based access control (Admin, Family Member, Guest)
- **Data Visualization**: Interactive charts and graphs with Plotly
- **Database Support**: SQLite for development, PostgreSQL for production
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modular Architecture**: Clean, maintainable code structure

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or Download the Project**
   ```bash
   # If using git
   git clone <repository-url>
   cd home_manager
   
   # Or extract the downloaded files
   cd home_manager
   ```

2. **Create Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Access the Application**
   - Open your web browser
   - Navigate to: `http://127.0.0.1:8000`
   - The application will automatically create the database and sample data

### Default Login
- **Username**: `admin`
- **Password**: `admin123`
- **⚠️ IMPORTANT**: Change the default password in production!

## 📊 Current Implementation Status

### ✅ Completed
- [x] Project structure and configuration
- [x] Database models and setup
- [x] User authentication system
- [x] Basic dashboard with sample data
- [x] Maintenance tracking models
- [x] Core utilities and helpers
- [x] Responsive web interface

### 🚧 In Development
- [ ] Complete maintenance management module
- [ ] Inventory management module
- [ ] Financial management module
- [ ] Task management module
- [ ] Document management module
- [ ] Advanced analytics module
- [ ] User management interface

## 🛠️ Development

### Running the Application
```bash
python app.py
```

The application will:
1. Initialize the database automatically
2. Create sample data for demonstration
3. Start the web server on `http://127.0.0.1:8000`

### Project Structure
- `app.py`: Main application entry point
- `config/`: Configuration and database setup
- `models/`: Database models for all features
- `utils/`: Utility functions and helpers
- `requirements.txt`: Python dependencies

---

**Built with ❤️ using Python Shiny**