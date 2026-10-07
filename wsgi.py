from app import create_app
from database import seed_database
from models import db

app = create_app()

with app.app_context():
    db.create_all()
    seed_database()

if __name__ == "__main__":
    app.run()
