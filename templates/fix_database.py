import os
from app import app, db
from datetime import datetime


def fix_database():
    print("🔧 Fixing database issues...")

    with app.app_context():
        try:
            # Drop all tables and recreate them
            db.drop_all()
            print("✅ Dropped all tables")

            db.create_all()
            print("✅ Recreated all tables")

            print("🎉 Database fixed successfully!")

        except Exception as e:
            print(f"❌ Error fixing database: {e}")


if __name__ == '__main__':
    fix_database()