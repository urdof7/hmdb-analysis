import psycopg2
from psycopg2 import sql
import sys
import os
from rdkit import Chem

def create_database():
    """
    Creates the hmdb_database if it does not exist.
    Uses environment variables for database credentials.
    """
    conn = psycopg2.connect(
        dbname="postgres",
        user=os.getenv("DB_USER"), #fetch DB_user from enviornment variables
        password=os.getenv("DB_PASSWORD"), #fetch from enviornment variables
        host=os.getenv("localhost"),
        port=os.getenv("5432")
    )
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        cursor.execute("CREATE DATABASE hmdb_database;")
        print("Database 'hmdb_database' created successfully.")
    except psycopg2.errors.DuplicateDatabase:
        print("Database 'hmdb_database' already exists.")
        # Prompt for action
        action = input("Do you want to (D)rop and recreate, (S)kip, or (Q)uit? ").strip().lower()
        if action == 'd':
            cursor.execute("DROP DATABASE hmdb_database;")
            cursor.execute("CREATE DATABASE hmdb_database;")
            print("Database 'hmdb_database' dropped and recreated.")
        elif action == 's':
            print("Skipping database creation.")
        else:
            print("Exiting.")
            sys.exit(0)
    finally:
        cursor.close()
        conn.close()

def connect_db():
    """
    Establishes a connection to the hmdb_database.
    """
    try:
        conn = psycopg2.connect(
            dbname="hmdb_database",
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        return conn
    except Exception as e:
        print("Unable to connect to the database 'hmdb_database'.")
        print(e)
        sys.exit(1)

def execute_sql_script(conn, sql_file):
    """
    Executes an SQL script to set up the database schema.
    """
    cursor = conn.cursor()
    with open(sql_file, 'r') as f:
        cursor.execute(f.read())
    conn.commit()
    cursor.close()
    print("Database schema created successfully.")

def parse_sdf(sdf_file):
    """
    Parses the SDF file using RDKit's SDMolSupplier.
    """
    suppl = Chem.SDMolSupplier(sdf_file)
    for mol in suppl:
        if mol is None:
            continue
        yield mol

def load_data(conn, sdf_file):
    """
    Loads data from the SDF file into the database.
    """
    cursor = conn.cursor()
    for mol in parse_sdf(sdf_file):
        # Get molecule properties
        hmdb_id = mol.GetProp('HMDB_ID') if mol.HasProp('HMDB_ID') else None
        generic_name = mol.GetProp('GENERIC_NAME') if mol.HasProp('GENERIC_NAME') else None
        formula = mol.GetProp('FORMULA') if mol.HasProp('FORMULA') else None
        molecular_weight = mol.GetProp('MOLECULAR_WEIGHT') if mol.HasProp('MOLECULAR_WEIGHT') else None
        exact_mass = mol.GetProp('EXACT_MASS') if mol.HasProp('EXACT_MASS') else None
        smiles = mol.GetProp('SMILES') if mol.HasProp('SMILES') else None
        inchi = mol.GetProp('INCHI_IDENTIFIER') if mol.HasProp('INCHI_IDENTIFIER') else None
        inchi_key = mol.GetProp('INCHI_KEY') if mol.HasProp('INCHI_KEY') else None

        # Insert into molecules table
        cursor.execute("""
            INSERT INTO molecules (hmdb_id, generic_name, formula, molecular_weight, exact_mass, smiles, inchi, inchi_key)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING molecule_id;
        """, (hmdb_id, generic_name, formula, molecular_weight, exact_mass, smiles, inchi, inchi_key))
        molecule_id = cursor.fetchone()[0]

        # Insert into structures table
        mol_block = Chem.MolToMolBlock(mol)
        atom_block, bond_block = extract_atom_bond_blocks(mol_block)
        cursor.execute("""
            INSERT INTO structures (molecule_id, atom_block, bond_block)
            VALUES (%s, %s, %s);
        """, (molecule_id, atom_block, bond_block))

        # Insert into properties table
        for prop_name in mol.GetPropNames():
            if prop_name not in ['HMDB_ID', 'GENERIC_NAME', 'FORMULA', 'MOLECULAR_WEIGHT', 'EXACT_MASS', 'SMILES', 'INCHI_IDENTIFIER', 'INCHI_KEY', 'SYNONYMS', 'JCHEM_IUPAC', 'JCHEM_TRADITIONAL_IUPAC']:
                prop_value = mol.GetProp(prop_name)
                cursor.execute("""
                    INSERT INTO properties (molecule_id, property_name, property_value)
                    VALUES (%s, %s, %s);
                """, (molecule_id, prop_name, prop_value))

        # Insert into synonyms table
        if mol.HasProp('SYNONYMS'):
            synonyms = mol.GetProp('SYNONYMS').split('; ')
            for synonym in synonyms:
                cursor.execute("""
                    INSERT INTO synonyms (molecule_id, synonym)
                    VALUES (%s, %s);
                """, (molecule_id, synonym))

        # Insert into names table
        name_types = ['JCHEM_IUPAC', 'JCHEM_TRADITIONAL_IUPAC']
        for name_type in name_types:
            if mol.HasProp(name_type):
                name = mol.GetProp(name_type)
                cursor.execute("""
                    INSERT INTO names (molecule_id, name_type, name)
                    VALUES (%s, %s, %s);
                """, (molecule_id, name_type, name))

        # Commit after each molecule (you can batch commits for performance)
        conn.commit()

    cursor.close()

def extract_atom_bond_blocks(mol_block):
    """
    Extracts atom and bond blocks from a molfile block.
    """
    lines = mol_block.split('\n')
    counts_line = lines[3]
    atom_count = int(counts_line[:3])
    bond_count = int(counts_line[3:6])

    atom_block = '\n'.join(lines[4:4 + atom_count])
    bond_block = '\n'.join(lines[4 + atom_count:4 + atom_count + bond_count])

    return atom_block, bond_block

def main():
    # Define file names
    sdf_file = 'structures.sdf'
    sql_file = 'create_hmdb_schema.sql'

    # Check if files exist in the current directory
    if not os.path.exists(sdf_file):
        print(f"File '{sdf_file}' does not exist in the current directory.")
        sys.exit(1)

    if not os.path.exists(sql_file):
        print(f"File '{sql_file}' does not exist in the current directory.")
        sys.exit(1)

    # Create the database
    create_database()

    # Connect to the hmdb_database
    conn = connect_db()

    # Execute the SQL script to create the schema
    execute_sql_script(conn, sql_file)

    # Load data into the database
    load_data(conn, sdf_file)
    conn.close()
    print("Data loading complete.")

if __name__ == '__main__':
    main()
