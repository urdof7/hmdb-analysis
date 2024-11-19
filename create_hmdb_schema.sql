-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS names;
DROP TABLE IF EXISTS synonyms;
DROP TABLE IF EXISTS properties;
DROP TABLE IF EXISTS structures;
DROP TABLE IF EXISTS molecules;

-- Create molecules table
CREATE TABLE molecules (
    molecule_id SERIAL PRIMARY KEY,
    hmdb_id VARCHAR(20) UNIQUE NOT NULL,
    generic_name VARCHAR(255),
    formula VARCHAR(50),
    molecular_weight FLOAT,
    exact_mass FLOAT,
    smiles TEXT,
    inchi TEXT,
    inchi_key VARCHAR(255)
);

-- Create structures table
CREATE TABLE structures (
    structure_id SERIAL PRIMARY KEY,
    molecule_id INTEGER REFERENCES molecules(molecule_id) ON DELETE CASCADE,
    atom_block TEXT,
    bond_block TEXT
);

-- Create properties table
CREATE TABLE properties (
    property_id SERIAL PRIMARY KEY,
    molecule_id INTEGER REFERENCES molecules(molecule_id) ON DELETE CASCADE,
    property_name VARCHAR(255),
    property_value VARCHAR(255)
);

-- Create synonyms table
CREATE TABLE synonyms (
    synonym_id SERIAL PRIMARY KEY,
    molecule_id INTEGER REFERENCES molecules(molecule_id) ON DELETE CASCADE,
    synonym VARCHAR(255)
);

-- Create names table
CREATE TABLE names (
    name_id SERIAL PRIMARY KEY,
    molecule_id INTEGER REFERENCES molecules(molecule_id) ON DELETE CASCADE,
    name_type VARCHAR(50),
    name VARCHAR(255)
);

-- Indexes to improve query performance
CREATE INDEX idx_molecules_hmdb_id ON molecules(hmdb_id);
CREATE INDEX idx_molecules_generic_name ON molecules(generic_name);
CREATE INDEX idx_synonyms_synonym ON synonyms(synonym);
CREATE INDEX idx_properties_property_name ON properties(property_name);
