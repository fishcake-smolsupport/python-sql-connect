from dotenv import dotenv_values
from typing import Tuple
from src.db import DatabaseConnector
from src.log import logger
import logging

CONFIG = dotenv_values(".env")
if not CONFIG:
    CONFIG = os.environ


@logger
def paneldata_show():
    incentive_env = DatabaseConnector(CONFIG['INC_KEY'])
    
    with open(CONFIG['PORTAL'], 'r') as file: 
        sql_statement = file.read()
        
    df = incentive_env.execute_query(sql_statement)
    return df

if __name__ == "__main__" :
    res = paneldata_show().astype(str)
    res.to_csv('out.csv', sep="|", index=False)
