import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import bcrypt
from config import DB_PATH, ADMIN_USERS, PUBLICATION_STATUSES, PUBLICATION_TYPES

class Database:
    def __init__(self):
        self.db_path = DB_PATH
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT,
                    group_name TEXT NOT NULL,
                    role TEXT DEFAULT 'group_head',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Research groups table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS research_groups (
                    group_name TEXT PRIMARY KEY,
                    department TEXT,
                    head_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_members INTEGER DEFAULT 0
                )
            ''')
            
            # Publications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS publications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paper_title TEXT NOT NULL,
                    authors TEXT NOT NULL,
                    corresponding_author TEXT,
                    journal_name TEXT,
                    submission_id TEXT UNIQUE,
                    status TEXT NOT NULL,
                    publication_type TEXT NOT NULL,
                    group_name TEXT NOT NULL,
                    submitted_by TEXT NOT NULL,
                    date_started DATE,
                    date_submitted DATE,
                    date_decision DATE,
                    doi TEXT,
                    impact_factor REAL,
                    notes TEXT,
                    manuscript_file TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_name) REFERENCES research_groups(group_name),
                    FOREIGN KEY (submitted_by) REFERENCES users(username)
                )
            ''')
            
            # Group meetings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS group_meetings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_name TEXT NOT NULL,
                    meeting_date DATE NOT NULL,
                    meeting_time TIME,
                    attendees TEXT,
                    agenda TEXT,
                    discussion_points TEXT,
                    action_items TEXT,
                    next_meeting_date DATE,
                    minutes_file TEXT,
                    created_by TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_name) REFERENCES research_groups(group_name),
                    FOREIGN KEY (created_by) REFERENCES users(username)
                )
            ''')
            
            # Activity log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES users(username)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_publications_group ON publications(group_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_publications_status ON publications(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_meetings_group_date ON group_meetings(group_name, meeting_date)')
            
            # Insert default admin user
            for username, user_data in ADMIN_USERS.items():
                hashed = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
                cursor.execute('''
                    INSERT OR IGNORE INTO users 
                    (username, password_hash, name, group_name, role)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, hashed, user_data['name'], user_data['group'], user_data['role']))
                
                cursor.execute('''
                    INSERT OR IGNORE INTO research_groups 
                    (group_name, department, head_name)
                    VALUES (?, ?, ?)
                ''', (user_data['group'], 'Administration', user_data['name']))
            
            conn.commit()
            print("Database initialized successfully")
            
        except Exception as e:
            print(f"Database initialization error: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def verify_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT username, password_hash, name, group_name, role, is_active FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            if not user:
                return False, "Invalid username or password", None
            if not user['is_active']:
                return False, "Account is deactivated", None
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
                cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?', (username,))
                conn.commit()
                user_data = {
                    'username': user['username'],
                    'name': user['name'],
                    'group_name': user['group_name'],
                    'role': user['role']
                }
                return True, "Login successful", user_data
            else:
                return False, "Invalid username or password", None
        except Exception as e:
            return False, f"Login error: {str(e)}", None
        finally:
            conn.close()
    
    def add_publication(self, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if not data.get('paper_title') or not data.get('authors'):
                return False, "Paper title and authors are required"
            
            cursor.execute('''
                INSERT INTO publications (
                    paper_title, authors, corresponding_author, journal_name,
                    submission_id, status, publication_type, group_name,
                    submitted_by, date_started, date_submitted, date_decision,
                    doi, impact_factor, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['paper_title'], data['authors'],
                data.get('corresponding_author', ''), data.get('journal_name', ''),
                data.get('submission_id', ''), data['status'],
                data['publication_type'], data['group_name'],
                data['submitted_by'], data.get('date_started'),
                data.get('date_submitted'), data.get('date_decision'),
                data.get('doi', ''), data.get('impact_factor', 0.0),
                data.get('notes', '')
            ))
            
            cursor.execute('''
                INSERT INTO activity_log (username, action, details)
                VALUES (?, ?, ?)
            ''', (data['submitted_by'], 'ADD_PUBLICATION', f"Added: {data['paper_title']}"))
            
            conn.commit()
            return True, f"Publication added successfully"
        except Exception as e:
            conn.rollback()
            return False, f"Error: {str(e)}"
        finally:
            conn.close()
    
    def get_group_stats(self, group_name):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) as count FROM publications WHERE group_name = ?', (group_name,))
            total = cursor.fetchone()['count']
            
            status_counts = {}
            for status in PUBLICATION_STATUSES:
                cursor.execute('SELECT COUNT(*) as count FROM publications WHERE group_name = ? AND status = ?', (group_name, status))
                status_counts[status] = cursor.fetchone()['count']
            
            in_progress = status_counts.get('In Preparation', 0) + status_counts.get('Submitted', 0) + status_counts.get('In Review', 0) + status_counts.get('Revision Requested', 0)
            accepted = status_counts.get('Accepted', 0)
            rejected = status_counts.get('Rejected', 0)
            total_decided = accepted + rejected
            acceptance_rate = round((accepted / total_decided * 100) if total_decided > 0 else 0, 1)
            
            cursor.execute('''
                SELECT strftime('%Y-%m', date_submitted) as month, COUNT(*) as count
                FROM publications WHERE group_name = ? AND date_submitted IS NOT NULL
                AND date_submitted >= date('now', '-12 months')
                GROUP BY month ORDER BY month
            ''', (group_name,))
            monthly_trend = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('''
                SELECT publication_type, COUNT(*) as count
                FROM publications WHERE group_name = ?
                GROUP BY publication_type
            ''', (group_name,))
            type_distribution = [dict(row) for row in cursor.fetchall()]
            
            return {
                'total': total,
                'in_progress': in_progress,
                'accepted': accepted,
                'rejected': rejected,
                'acceptance_rate': acceptance_rate,
                'status_counts': status_counts,
                'monthly_trend': monthly_trend,
                'type_distribution': type_distribution
            }
        except Exception as e:
            print(f"Error getting group stats: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_publications(self, group_name=None, status=None, date_range=None):
        conn = self.get_connection()
        try:
            query = "SELECT * FROM publications WHERE 1=1"
            params = []
            if group_name:
                query += " AND group_name = ?"
                params.append(group_name)
            if status:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY updated_at DESC"
            df = pd.read_sql_query(query, conn, params=params)
            return df
        except Exception as e:
            print(f"Error getting publications: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def add_group_meeting(self, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO group_meetings (group_name, meeting_date, meeting_time, attendees, agenda, discussion_points, action_items, next_meeting_date, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['group_name'], data['meeting_date'],
                data.get('meeting_time', ''), data.get('attendees', ''),
                data.get('agenda', ''), data.get('discussion_points', ''),
                data.get('action_items', ''), data.get('next_meeting_date'),
                data.get('created_by', '')
            ))
            conn.commit()
            return True, "Meeting added successfully"
        except Exception as e:
            conn.rollback()
            return False, f"Error: {str(e)}"
        finally:
            conn.close()
    
    def add_user(self, username, password, name, email, group_name, role='group_head'):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if not all([username, password, name, group_name]):
                return False, "All required fields must be filled"
            
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return False, "Username already exists"
            
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                INSERT INTO users (username, password_hash, name, email, group_name, role)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, name, email, group_name, role))
            
            cursor.execute('INSERT OR IGNORE INTO research_groups (group_name, head_name) VALUES (?, ?)', (group_name, name))
            
            conn.commit()
            return True, f"User created successfully"
        except Exception as e:
            conn.rollback()
            return False, f"Error: {str(e)}"
        finally:
            conn.close()
    
    def delete_publication(self, publication_id, username, user_role):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if user_role != 'admin':
                return False, "Only administrators can delete publications"
            cursor.execute("DELETE FROM publications WHERE id = ?", (publication_id,))
            cursor.execute('INSERT INTO activity_log (username, action, details) VALUES (?, ?, ?)', (username, 'DELETE_PUBLICATION', f"Deleted ID: {publication_id}"))
            conn.commit()
            return True, "Publication deleted successfully"
        except Exception as e:
            conn.rollback()
            return False, f"Error: {str(e)}"
        finally:
            conn.close()
    
    def get_users_by_group(self, group_name=None):
        conn = self.get_connection()
        try:
            if group_name:
                df = pd.read_sql_query("SELECT * FROM users WHERE group_name = ? AND is_active = 1", conn, params=[group_name])
            else:
                df = pd.read_sql_query("SELECT * FROM users WHERE is_active = 1", conn)
            return df
        except Exception as e:
            print(f"Error getting users: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def export_data(self, group_name=None, format='csv'):
        df = self.get_all_publications(group_name)
        if df.empty:
            return None, "No data to export"
        try:
            if format == 'csv':
                return df.to_csv(index=False), "publications_export.csv"
            elif format == 'excel':
                import io
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Publications', index=False)
                return output.getvalue(), "publications_export.xlsx"
        except Exception as e:
            return None, f"Export error: {str(e)}"