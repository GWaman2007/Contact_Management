"""
Seed script to create a sample user and demo contacts (including normal and hidden contacts).
Run: python seed_demo.py
"""
from app import app, db
from models import User, Contact

def seed_database():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        print("--> Creating test user...")
        user = User(name="Alex Johnson", email="alex@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        print(f"--> User created! Email: alex@example.com | Password: password123 | User ID: {user.user_id}")

        print("--> Adding sample contacts...")

        # Normal contacts
        c1 = Contact(
            user_id=user.user_id,
            name="Sarah Jenkins",
            ph_no="+1-555-0192",
            email="sarah.j@acme.com",
            company_name="Acme Corporation"
        )
        c2 = Contact(
            user_id=user.user_id,
            name="Robert Chen",
            ph_no="+1-555-0144",
            email="robert@techsoft.io",
            company_name="TechSoft"
        )

        # Hidden contact with hide_code
        c3_hidden = Contact(
            user_id=user.user_id,
            name="Vanguard Classified",
            ph_no="+1-800-SECRET",
            email="classified@vanguard.org",
            company_name="Vanguard Project",
            hide_code="OP77"
        )

        db.session.add_all([c1, c2, c3_hidden])
        db.session.commit()

        print("--> Seed data successfully added!")
        print("--> 2 Normal contacts created.")
        print("--> 1 Hidden contact created (Hide Code: OP77).")

if __name__ == '__main__':
    seed_database()
