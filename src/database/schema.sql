-- Dijital Risk Analiz Formu SQLite Şeması

CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    synthetic_code TEXT UNIQUE NOT NULL,
    company_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    city TEXT NOT NULL,
    district TEXT NOT NULL,
    address TEXT,
    insured_value REAL DEFAULT 0.0,
    hazard_class TEXT DEFAULT 'Orta'
);

CREATE TABLE IF NOT EXISTS inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    inspector_name TEXT NOT NULL,
    inspection_date TEXT NOT NULL,
    occupancy_type TEXT,
    building_construction TEXT,
    total_area_sqm REAL DEFAULT 0.0,
    number_of_floors INTEGER DEFAULT 1,
    fire_measures TEXT,          -- JSON string
    security_measures TEXT,      -- JSON string
    natural_hazard_measures TEXT,-- JSON string
    calculated_risk_score REAL DEFAULT 0.0,
    risk_level TEXT,
    ai_executive_summary TEXT,
    ai_recommendations TEXT,
    uw_notes TEXT,
    status TEXT DEFAULT 'Taslak',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS inspection_photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inspection_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    category TEXT DEFAULT 'Genel',
    caption TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inspection_id INTEGER NOT NULL,
    priority TEXT DEFAULT 'Orta',
    category TEXT DEFAULT 'Yangın',
    finding TEXT NOT NULL,
    action_required TEXT NOT NULL,
    target_deadline_days INTEGER DEFAULT 30,
    status TEXT DEFAULT 'Açık',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE
);
