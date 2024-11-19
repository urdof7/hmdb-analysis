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
    generic_name TEXT,
    formula VARCHAR(50),
    molecular_weight FLOAT,
    exact_mass FLOAT,
    smiles TEXT,
    inchi TEXT,
    inchi_key TEXT
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
    synonym TEXT
);

-- Create names table
CREATE TABLE names (
    name_id SERIAL PRIMARY KEY,
    molecule_id INTEGER REFERENCES molecules(molecule_id) ON DELETE CASCADE,
    name_type VARCHAR(50),
    name TEXT
);


-- View for quick access to basic molecule information without needing a full query on the table
CREATE VIEW basic_molecule_info AS
SELECT hmdb_id, generic_name, molecular_weight, smiles, inchi_key
FROM molecules;

-- View for full molecule details with related names, synonyms, properties, and structure data
-- This view consolidates data across multiple tables, making it easier to access complete information without repeatedly joining tables.
CREATE VIEW full_molecule_info AS
SELECT 
    m.hmdb_id, m.generic_name, m.formula, m.molecular_weight, m.exact_mass,
    s.synonym, n.name_type, n.name,
    p.property_name, p.property_value,
    st.atom_block, st.bond_block
FROM molecules m
LEFT JOIN synonyms s ON m.molecule_id = s.molecule_id
LEFT JOIN names n ON m.molecule_id = n.molecule_id
LEFT JOIN properties p ON m.molecule_id = p.molecule_id
LEFT JOIN structures st ON m.molecule_id = st.molecule_id;

-- View to display properties associated with each molecule 
CREATE VIEW molecule_properties AS
SELECT m.hmdb_id, m.generic_name, p.property_name, p.property_value
FROM molecules m
JOIN properties p ON m.molecule_id = p.molecule_id;

-- View to display structure information for each molecule
CREATE VIEW molecule_structures AS
SELECT m.hmdb_id, m.generic_name, s.atom_block, s.bond_block
FROM molecules m
JOIN structures s ON m.molecule_id = s.molecule_id;

-- View to display synonyms associated with each molecule
CREATE VIEW molecule_synonyms AS
SELECT m.hmdb_id, m.generic_name, s.synonym
FROM molecules m
JOIN synonyms s ON m.molecule_id = s.molecule_id;


-- Indexes to improve join performance created on foreign key columns in the child tables
CREATE INDEX synonyms_molecule_id_index ON synonyms(molecule_id);
CREATE INDEX names_molecule_id_index ON names(molecule_id);
CREATE INDEX properties_molecule_id_index ON properties(molecule_id);
CREATE INDEX structures_molecule_id_index ON structures(molecule_id);

-- Indexes to accelerate searches by common fields created on columns I expect to be frequently used in search conditions.
CREATE INDEX molecules_generic_name_index ON molecules(generic_name);
CREATE INDEX synonyms_synonym_index ON synonyms(synonym);
CREATE INDEX names_name_index ON names(name);
CREATE INDEX properties_property_name_index ON properties(property_name);
CREATE INDEX molecules_inchi_key_index ON molecules(inchi_key);
CREATE INDEX molecules_smiles_index ON molecules(smiles);





