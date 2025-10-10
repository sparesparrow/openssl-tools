-- Enhanced schema with component tracking
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE components (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    type VARCHAR(20), -- 'library', 'executable', 'header-only'
    dependencies JSONB,
    build_targets JSONB,
    configure_options JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, version)
);

CREATE TABLE builds (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    component_id INTEGER REFERENCES components(id),
    version VARCHAR(50) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    profile VARCHAR(20) NOT NULL,
    build_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    commit_sha VARCHAR(40),
    build_host VARCHAR(100),
    conan_version VARCHAR(50),
    status VARCHAR(20) DEFAULT 'building',
    build_duration_seconds INTEGER,
    error_message TEXT,
    build_log TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial components
INSERT INTO components (name, version, description, type, dependencies, build_targets, configure_options) VALUES
('openssl-crypto', '3.2.0', 'OpenSSL cryptographic library component', 'library', 
 '["zlib"]', '["libcrypto.so", "libcrypto.a"]', '["no-ssl3", "no-comp", "no-hw", "no-engine", "no-dso"]'),
('openssl-ssl', '3.2.0', 'OpenSSL SSL/TLS library component', 'library',
 '["openssl-crypto"]', '["libssl.so", "libssl.a"]', '["no-comp", "no-hw", "no-engine"]'),
('openssl-tools', '3.2.0', 'OpenSSL command-line tools and utilities', 'executable',
 '["openssl-ssl"]', '["openssl", "ca", "ciphers", "cms"]', '[]');
