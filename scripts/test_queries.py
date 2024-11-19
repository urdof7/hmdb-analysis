import psycopg2
import os

def connect_db():
    """
    Establishes a connection to the hmdb_database using environment variables.
    """
    conn = psycopg2.connect(
        dbname="hmdb_database",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=("localhost"),
        port=("5432")
    )
    return conn

def run_query(conn, query, description=""):
    """
    Runs a specified query and prints the results with a description.
    """
    cursor = conn.cursor()
    print(f"\n{description}")
    cursor.execute(query)
    results = cursor.fetchall()
    
    # Check if the result has only one row with one column
    if len(results) == 1 and len(results[0]) == 1:
        print(results[0][0])  # Print the single value directly
    else:
        for row in results:
            print(row)
    
    cursor.close()

def main():
    conn = connect_db()
    try:
        run_query(conn, """
            SELECT COUNT(*) AS total_molecules FROM molecules;
        """, description="Total number of molecules in the database:")

        # Example queries
        run_query(conn, """
            SELECT molecule_id, hmdb_id, generic_name, molecular_weight 
            FROM molecules 
            LIMIT 5;
        """, description="Showing basic molecule information for the first 5 entries:")

        run_query(conn, """
            SELECT smiles, inchi, inchi_key 
            FROM molecules 
            WHERE hmdb_id = 'HMDB0008301';
        """, description="Retrieving SMILES, InChI, and InChI Key for HMDB0008301:")

        run_query(conn, """
            SELECT synonym 
            FROM synonyms 
            WHERE molecule_id = 407;
        """, description="Listing all synonyms for molecule_id 407:")

        run_query(conn, """
            SELECT hmdb_id, generic_name, molecular_weight 
            FROM molecules 
            WHERE molecular_weight IS NOT NULL 
            ORDER BY molecular_weight DESC 
            LIMIT 5;
        """, description="Top 5 heaviest molecules by molecular weight:")

    finally:
        conn.close()

if __name__ == '__main__':
    main()
