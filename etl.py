import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


def load_staging_tables(cur, conn):
    """
    Run all COPY commands to extract data from JSON files and copy into staging tables.
    """        
        print('Execute: load_staging_tables()')
        for query in copy_table_queries:
                cur.execute(query)
                conn.commit()
        print('DONE!')

def insert_tables(cur, conn):
    """
    Run all INSERT SQL statements to copy data from staging tables to fact and dimension tables.
    """            
        print('Execute: insert_tables()')
        for query in insert_table_queries:
                cur.execute(query)
                conn.commit()
        print('DONE!')


def main():
    """
    Connect to Redshift database, then execute functions to copy data from S3 to staging tables 
    and transfer data from staging to fact and dimension tables.
    """          
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    
    load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()