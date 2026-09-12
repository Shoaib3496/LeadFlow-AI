from database.db import SessionLocal
from database.models import Source

db = SessionLocal()

sources = db.query(Source).all()

for source in sources:
    print(source.__dict__)

db.close()