#!/usr/bin/env python3

import os
import argparse
from dotenv import dotenv_values
from src.db import DatabaseConnector
from src.log import logger
import logging

CONFIG = dotenv_values(".env")
if not CONFIG:
    CONFIG = os.environ

@logger
def paneldata_show(database_key: str, execute_write: bool = False):
    incentive_env = DatabaseConnector(CONFIG[database_key])
    
    with open(CONFIG['PORTAL'], 'r') as file: 
        sql_statement = file.read()

    if execute_write:
        # Assuming the SQL statement is safe and intended for execution
        result = incentive_env.execute_commit(sql_statement)
        
        logging.info(f'Write request \n{sql_statement}\n\nhas been executed successfully.')
        return None
    else:
        df = incentive_env.execute_query(sql_statement)
        return df

def main(database_key: str, execute_write: bool):
    res = paneldata_show(database_key, execute_write)
    
    if execute_write:
        logging.info("Write operation executed successfully.")
    else:
        res.to_csv('out.csv', sep="|", index=False, na_rep="")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute SQL commands.")
    parser.add_argument(
        '--db', 
        type=str, 
        required=True, 
        help='Database key to use from the .env file (e.g., PRD, STG, DEV, etc.).'
    )
    parser.add_argument(
        '--ex', 
        action='store_true', 
        help='Execute write operations (INSERT, UPDATE, DELETE).'
    )
    
    args = parser.parse_args()
    main(args.db, args.ex)
