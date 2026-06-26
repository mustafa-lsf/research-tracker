# Configuration settings
import os

# Database configuration
DB_PATH = os.path.join("data", "research.db")

# App settings
APP_NAME = "Lahore Science Foundry"
APP_SUBTITLE = "Khwarizmi Science Society - Research Tracker"
APP_ICON = "🧪"

# Session timeout in minutes
SESSION_TIMEOUT = 60

# Default admin credentials (change these in production!)
ADMIN_USERS = {
    "admin": {
        "name": "System Administrator",
        "group": "KSS Admin",
        "password": "Admin@KSS2024",
        "role": "admin"
    }
}

# Publication statuses
PUBLICATION_STATUSES = [
    "In Preparation",
    "Submitted",
    "In Review",
    "Revision Requested",
    "Accepted",
    "Rejected"
]

# Publication types
PUBLICATION_TYPES = [
    "Original Research",
    "Review Article",
    "Case Study",
    "Methodology Paper",
    "Short Communication",
    "Book Chapter",
    "Conference Paper",
    "Preprint"
]

# Color scheme for statuses
STATUS_COLORS = {
    "In Preparation": "#FFA726",
    "Submitted": "#42A5F5",
    "In Review": "#AB47BC",
    "Revision Requested": "#EF5350",
    "Accepted": "#66BB6A",
    "Rejected": "#BDBDBD"
}