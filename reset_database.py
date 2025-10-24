import os
from app import app, db, User, Announcement, Question, Answer


def reset_database():
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()

        print("Creating all tables with updated schema...")
        db.create_all()

        # Optional: Create a test coordinator user
        try:
            coordinator = User(
                username='admin',
                email='admin@ojotounion.com',
                role='coordinator'
            )
            coordinator.set_password('admin123')
            db.session.add(coordinator)
            db.session.commit()
            print("Created test coordinator: admin / admin123")
        except:
            db.session.rollback()
            print("Test coordinator already exists or couldn't be created")

        print("Database reset successfully!")
        print("All tables recreated with the role column.")


if __name__ == '__main__':
    reset_database()