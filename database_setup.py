import sqlite3
import bcrypt
import os
from pathlib import Path

def create_database():
    """Initialize the SQLite database with all required tables"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    db_path = project_root / 'attendance.db'
    
    print(f"📁 Creating database at: {db_path}")
    
    # Create database connection
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            fingerprint_id INTEGER UNIQUE,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Created 'users' table")
    
    # Create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('IN', 'OUT')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    print("✅ Created 'attendance' table")
    
    # Create admins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Created 'admins' table")
    
    # Check if default admin already exists
    cursor.execute("SELECT COUNT(*) FROM admins WHERE username = ?", ("admin",))
    admin_exists = cursor.fetchone()[0] > 0
    
    if not admin_exists:
        # Create default admin account (username: admin, password: admin123)
        default_password = "admin123"
        password_hash = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())
        
        try:
            cursor.execute(
                "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
                ("admin", password_hash)
            )
            print("✅ Default admin created: username='admin', password='admin123'")
        except sqlite3.IntegrityError:
            print("ℹ️  Default admin already exists")
    else:
        print("ℹ️  Default admin already exists")
    
    # Create assets directory for user images
    assets_dir = project_root / 'assets'
    user_images_dir = assets_dir / 'user_images'
    
    if not assets_dir.exists():
        assets_dir.mkdir()
        print("✅ Created 'assets' directory")
    
    if not user_images_dir.exists():
        user_images_dir.mkdir()
        print("✅ Created 'assets/user_images' directory")
    
    # Commit changes and close
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ Database created successfully!")
    print(f"📁 Database file: {db_path}")
    print(f"📂 Assets folder: {user_images_dir}")
    print("\n🔐 Default Login Credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("="*60)
    
    return str(db_path)

if __name__ == "__main__":
    db_path = create_database()
    print(f"\n✨ Setup complete! Database is ready at: {db_path}")