from sqlalchemy import inspect

from database import engine


inspector = inspect(engine)

tables = inspector.get_table_names()

print("\nTables in database:")
for table in tables:
    print("-", table)

print("\nUsers columns:")
for column in inspector.get_columns("users"):
    print("-", column["name"])

print("\nUser conditions columns:")
for column in inspector.get_columns("user_conditions"):
    print("-", column["name"])

print("\nAnalyses columns:")
for column in inspector.get_columns("analyses"):
    print("-", column["name"])