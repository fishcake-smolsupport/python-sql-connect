import logging
import pandas as pd
from sqlalchemy import create_engine, exc, text

class DatabaseConnector:
    def __init__(self, database_url: str):
        """
        Initialize DatabaseConnector with a database URL.
        
        :param database_url: Database URL for connecting to the target database.
        """
        self.database_url = database_url
        self.engine = self._create_engine()

    def _create_engine(self):
        """Create and return a SQLAlchemy engine."""
        try:
            engine = create_engine(self.database_url)
            return engine
        except exc.SQLAlchemyError as e:
            print(f"Error: SQLAlchemy connection failed. {e}")
            return None

    def execute_query(self, statement: str, batch_size=1000) -> pd.DataFrame:
        """Executes a SQL query and returns a DataFrame."""
        if not self.engine:
            print("Error: No engine established.")
            return pd.DataFrame()  # Return an empty DataFrame in case of failure

        frames = []  # To store chunks of DataFrame
        try:
            with self.engine.connect() as connection:
                result_proxy = connection.execute(text(statement))

                # Fetch rows in chunks and add to frames
                column_names = result_proxy.keys()
                while True:
                    rows = result_proxy.fetchmany(batch_size)
                    if not rows:
                        break
                    frames.append(pd.DataFrame(rows, columns=column_names))

                # Concatenate all frames to form the final DataFrame
                if frames:
                    df = pd.concat(frames, ignore_index=True)
                    logging.info(f"Data retrieved successfully: {df.shape}")
                    return df
                else:
                    print("No data retrieved.")
                    return pd.DataFrame(columns=column_names)
                
        except exc.SQLAlchemyError as e:
            str_e = str(e)
            err = "\n".join(str_e.splitlines()[:3])
            print(f"Error executing query: {err}")
            return pd.DataFrame()

    def execute_commit(self, statement: str) -> bool:
        """Executes a commit SQL query (INSERT, UPDATE, DELETE). Returns True if successful."""
        if not self.engine:
            print("Error: No engine established.")
            return False

        try:
            with self.engine.connect() as connection:
                transaction = connection.begin()
                connection.execute(text(statement))
                transaction.commit()
            return True
        
        except exc.SQLAlchemyError as e:
            str_e = str(e)
            err = "\n".join(str_e.splitlines()[:3])
            print(f"Error executing commit query: {err}")
            if 'transaction' in locals():
                transaction.rollback()
            return False

# Sample Usage
# CONFIG = dotenv_values(".env")
# production_env = DatabaseConnector(CONFIG['PRD_KEY'])
