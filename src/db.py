from sqlalchemy import create_engine, exc, text
import pandas as pd

# class ResultSet:
#     def __init__(self, result_proxy, batch_size=1000):
#         """
#         Initialize ResultSet with a result proxy and optional batch size for chunking.
        
#         :param result_proxy: The result set proxy from SQLAlchemy query execution.
#         :param batch_size: Number of rows to retrieve per chunk.
#         """
#         self.result_proxy = result_proxy
#         self.batch_size = batch_size
#         self.column_names = result_proxy.keys() if result_proxy else []

#     def as_dataframe(self) -> pd.DataFrame:
#         """Convert the result proxy to a DataFrame in manageable chunks."""
#         frames = []
#         if self.result_proxy is None:
#             print("Error: No results to convert.")
#             return pd.DataFrame()

#         # Fetch rows in chunks and add to frames
#         while True:
#             rows = self.result_proxy.fetchmany(self.batch_size)
#             if not rows:
#                 break
#             frames.append(pd.DataFrame(rows, columns=self.column_names))

#         # Return empty DataFrame if frames are empty, avoiding concat error
#         if not frames:
#             print("No data retrieved.")
#             return pd.DataFrame(columns=self.column_names)
        
#         return pd.concat(frames, ignore_index=True)


class DatabaseConnector:
    def __init__(self, database_url: str):
        """
        Initialize DatabaseConnector with a database URL.
        
        :param database_url: Database URL for connecting to the target database.
        """
        self.database_url = database_url
        self.engine = self._create_engine()
        self.result_set = None  # Initialize an empty result_set attribute

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
                    return pd.concat(frames, ignore_index=True)
                else:
                    print("No data retrieved.")
                    return pd.DataFrame(columns=column_names)
                
        except exc.SQLAlchemyError as e:
            print(f"Error executing query: {e}")
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
            print(f"Error executing commit query: {e}")
            if 'transaction' in locals():
                transaction.rollback()
            return False

# Sample Usage
# CONFIG = dotenv_values(".env")
# production_env = DatabaseConnector(CONFIG['PRD_KEY'])
