from sqlalchemy import inspect, text

from database import engine, Base
import models


def upgrade_database():
    print("Starting database upgrade...")

    # Create all new tables that don't already exist.
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)

    # Check existing columns in the analyses table.
    analysis_columns = {
        column["name"]
        for column in inspector.get_columns("analyses")
    }

    # Add user_id to the existing analyses table if necessary.
    if "user_id" not in analysis_columns:
        print("Adding user_id column to analyses table...")

        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    ALTER TABLE analyses
                    ADD COLUMN user_id INTEGER
                    """
                )
            )

        print("user_id column added successfully.")

    else:
        print("user_id column already exists.")

    print("Database upgrade completed successfully.")


if __name__ == "__main__":
    upgrade_database()