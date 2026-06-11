-- StackAlert — D1 (SQLite) schema, ingestion side only.
-- Account/billing tables come later (S7+); keep the validation phase lean.

CREATE TABLE IF NOT EXISTS cves (
  id            TEXT PRIMARY KEY,          -- "CVE-2026-12345"
  published     TEXT NOT NULL,             -- ISO 8601
  last_modified TEXT NOT NULL,
  cvss_score    REAL,
  cvss_severity TEXT,                      -- LOW/MEDIUM/HIGH/CRITICAL
  description   TEXT,
  cpe_json      TEXT,                      -- raw CPE match criteria (JSON) for the matcher
  in_kev        INTEGER NOT NULL DEFAULT 0,
  kev_date_added TEXT,
  epss_score    REAL,                      -- 0..1, probability of exploitation in 30 days
  epss_fetched_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_cves_last_modified ON cves(last_modified);
CREATE INDEX IF NOT EXISTS idx_cves_kev ON cves(in_kev);

-- Curated product catalog (launch with ~200-500 well-mapped products,
-- NOT the whole NVD CPE dictionary — quality of matching beats coverage).
CREATE TABLE IF NOT EXISTS products (
  id        INTEGER PRIMARY KEY,
  vendor    TEXT NOT NULL,                 -- cpe vendor segment, e.g. "fortinet"
  product   TEXT NOT NULL,                 -- cpe product segment, e.g. "fortios"
  display   TEXT NOT NULL,                 -- "Fortinet FortiOS"
  UNIQUE(vendor, product)
);

-- Ingestion bookkeeping (cursor for NVD incremental sync).
CREATE TABLE IF NOT EXISTS sync_state (
  source     TEXT PRIMARY KEY,             -- 'nvd' | 'kev' | 'epss'
  cursor     TEXT,                         -- e.g. last lastModEndDate used
  updated_at TEXT
);
