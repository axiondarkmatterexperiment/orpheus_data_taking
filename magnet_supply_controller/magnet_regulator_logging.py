import psycopg2

def create_magnet_regulator_table():
    ''' 
    Set up connection to the psql database
    '''

    # define the connection to the postgres database
    # conn = psycopg2.connect(host='192.168.25.2', dbname='postgres', user='admx_master', password='wimpssuck', port=5432)
    conn = psycopg2.connect(host='192.168.25.2', dbname='orpheus_db', user='postgres', password='axionsrock', port=5432)

    #I think this is just what we use to send commands directly to the postgres command line
    cur = conn.cursor()
    
    cur.execute("""CREATE TABLE IF NOT EXISTS public.magnet_regulator (
                sensor_name TEXT,
                "timestamp" TIMESTAMPTZ,
                val_raw REAL,
                val_cal REAL
                );
                """)
    
    conn.commit()
    
    cur.close()
    conn.close()

def log_magnet_regulator_value(sensor_name, timestamp, val_raw, val_cal ):
    ''' 
    Set up connection to the psql database
    '''

    # define the connection to the postgres database
    # conn = psycopg2.connect(host='192.168.25.2', dbname='postgres', user='admx_master', password='wimpssuck', port=5432)
    conn = psycopg2.connect(host='192.168.25.2', dbname='orpheus_db', user='postgres', password='axionsrock', port=5432)

    #I think this is just what we use to send commands directly to the postgres command line
    cur = conn.cursor()

    cur.execute("INSERT INTO magnet_regulator (sensor_name, timestamp, val_raw, val_cal) VALUES (%s, %s, %s, %s)",
                (sensor_name, timestamp, val_raw, val_cal))
    
    conn.commit()
    
    cur.close()
    conn.close()
