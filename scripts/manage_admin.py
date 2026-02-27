import sys
import os

# Add parent directory to path so we can import from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth_server import app
from models import db, User

def create_admin(username, email, password):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User {username} already exists. Promoting to admin and resetting password...")
            user.is_admin = True
            user.set_password(password)
        else:
            user = User(username=username, email=email, is_admin=True)
            user.set_password(password)
            db.session.add(user)
        
        db.session.commit()
        print(f"Successfully set {username} as Admin.")

def list_users():
    with app.app_context():
        users = User.query.all()
        print("\n--- User List ---")
        for u in users:
            status = "[ADMIN]" if u.is_admin else "[USER]"
            print(f"ID: {u.id} | Username: {u.username} | Email: {u.email} | Status: {status}")
        print("-----------------\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_admin.py create <username> <email> <password>")
        print("  python manage_admin.py list")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) != 5:
            print("Error: Missing arguments for create.")
            print("Usage: python manage_admin.py create <username> <email> <password>")
            sys.exit(1)
        create_admin(sys.argv[2], sys.argv[3], sys.argv[4])
    elif command == "list":
        list_users()
    else:
        print(f"Unknown command: {command}")
