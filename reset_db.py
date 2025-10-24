import os
from app import app, db

with app.app_context():
    # Drop all tables
    db.drop_all()
    print("🗑️  All tables dropped")

    # Create all tables
    db.create_all()
    print("✅ All tables created successfully")

    print("🔄 Database reset complete!")
    # Create new database with updated schema
    with app.app_context():
        db.create_all()
        print("✅ Created new database with updated schema")

        # Create sample users for testing
        try:
            # Create a coordinator
            coordinator = User(
                username='coordinator',
                email='coordinator@ojoto.com',
                role='coordinator'
            )
            coordinator.set_password('password123')
            db.session.add(coordinator)

            # Create a student
            student = User(
                username='student',
                email='student@ojoto.com',
                role='student'
            )
            student.set_password('password123')
            db.session.add(student)

            db.session.commit()
            print("✅ Created test users:")
            print("   👨‍💼 Coordinator: coordinator / password123")
            print("   👨‍🎓 Student: student / password123")

        except Exception as e:
            print(f"⚠️  Could not create test users: {e}")

    print("🎉 Database reset complete!")
    print("🚀 You can now run: python app.py")


if __name__ == '__main__':
    reset_database()