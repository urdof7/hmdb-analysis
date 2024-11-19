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
        host="localhost",
        port="5432"
    )
    return conn

def run_query(conn, query, file, description=""):
    """
    Runs a specified query and writes the results to a file with a description.
    """
    cursor = conn.cursor()
    file.write(f"\n{description}\n")
    cursor.execute(query)
    results = cursor.fetchall()
    
    # Check if the result has only one row with one column
    if len(results) == 1 and len(results[0]) == 1:
        file.write(f"{results[0][0]}\n")  # Write the single value directly
    else:
        for row in results:
            file.write(f"{row}\n")
        
    cursor.close()

def main():
    conn = connect_db()
    try:
        with open("query_results.txt", "w") as file:  # Open the file in write mode
            # Retrieve SMILES strings for molecules with molecular_weight between 160 and 161.
            run_query(conn, """
                SELECT hmdb_id, generic_name, molecular_weight, smiles
                FROM basic_molecule_info
                WHERE molecular_weight BETWEEN 160 AND 161
                LIMIT 3;
            """, file, description="SMILES strings for molecules with molecular weight between 160 and 161:")

            # Retrieve SMILES strings for molecules with a neutral formal charge.
            run_query(conn, """
                SELECT m.hmdb_id, m.generic_name, m.smiles, charge.property_value AS formal_charge
                FROM molecules m
                JOIN properties charge ON m.molecule_id = charge.molecule_id AND charge.property_name = 'JCHEM_FORMAL_CHARGE'
                WHERE charge.property_value = '0'
                LIMIT 3;
            """, file, description="SMILES strings for molecules with a neutral formal charge:")

            # Retrieve SMILES strings for molecules whose generic_name contains the word 'acid'.
            run_query(conn, """
                SELECT hmdb_id, generic_name, smiles
                FROM basic_molecule_info
                WHERE generic_name ILIKE '%acid%'
                LIMIT 3;
            """, file, description="SMILES strings for molecules whose generic_name contains 'acid':")

            # Retrieve SMILES strings for molecules that have a synonym containing 'glucose'.
            run_query(conn, """
                SELECT DISTINCT m.hmdb_id, m.generic_name, m.smiles
                FROM molecules m
                JOIN synonyms s ON m.molecule_id = s.molecule_id
                WHERE s.synonym ILIKE '%glucose%'
                LIMIT 3;
            """, file, description="SMILES strings for molecules with a synonym containing 'glucose':")

            # Count of entries in each table (molecules, synonyms, properties, structures, names).
            run_query(conn, """
                SELECT 
                    (SELECT COUNT(*) FROM molecules) AS num_molecules,
                    (SELECT COUNT(*) FROM synonyms) AS num_synonyms,
                    (SELECT COUNT(*) FROM properties) AS num_properties,
                    (SELECT COUNT(*) FROM structures) AS num_structures,
                    (SELECT COUNT(*) FROM names) AS num_names;
            """, file, description="Count of elements in each table (molecules, synonyms, properties, structures, names):")

            # Molecules with synonyms containing 'cholesterol'.
            run_query(conn, """
                SELECT DISTINCT hmdb_id, generic_name, synonym
                FROM molecule_synonyms
                WHERE synonym ILIKE '%cholesterol%'
                LIMIT 3;
            """, file, description="Molecules with synonyms containing 'cholesterol':")

            # Structure information for a random molecule.
            run_query(conn, """
                SELECT hmdb_id, generic_name, atom_block, bond_block
                FROM molecule_structures
                ORDER BY RANDOM()
                LIMIT 1;
            """, file, description="Structure information for a random molecule:")

            # Molecules where generic_name starts with 'L-'.
            run_query(conn, """
                SELECT hmdb_id, generic_name, molecular_weight
                FROM basic_molecule_info
                WHERE generic_name LIKE 'L-%'
                LIMIT 3;
            """, file, description="Molecules where the generic_name starts with 'L-':")

            # Percentage of molecules that comply with Veber's rule.
            run_query(conn, """
                SELECT ROUND(
                    (SELECT COUNT(*) FROM properties WHERE property_name = 'JCHEM_VEBER_RULE' AND property_value = '1')::numeric /
                    (SELECT COUNT(*) FROM molecules) * 100, 2
                ) AS veber_rule_compliance_percent;
            """, file, description="Percentage of molecules that comply with Veber's rule:")

    finally:
        conn.close()

if __name__ == '__main__':
    main()
