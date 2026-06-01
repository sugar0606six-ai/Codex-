CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL DEFAULT 'analyst',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS catalog_products (
  id SERIAL PRIMARY KEY,
  sku VARCHAR(120) UNIQUE NOT NULL,
  name VARCHAR(500) NOT NULL,
  category VARCHAR(255),
  cost DOUBLE PRECISION,
  sale_price DOUBLE PRECISION,
  inventory INTEGER,
  weight VARCHAR(120),
  dimensions VARCHAR(120),
  variants JSONB,
  description TEXT,
  images JSONB,
  supplier VARCHAR(255) DEFAULT 'WestMonth',
  source_url VARCHAR(1000),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS search_keywords (
  id SERIAL PRIMARY KEY,
  keyword VARCHAR(255) NOT NULL,
  category VARCHAR(255),
  status VARCHAR(50) NOT NULL DEFAULT 'queued',
  requested_by INTEGER REFERENCES users(id),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS amazon_products (
  id SERIAL PRIMARY KEY,
  asin VARCHAR(30),
  title VARCHAR(700) NOT NULL,
  category VARCHAR(255),
  price DOUBLE PRECISION,
  rating DOUBLE PRECISION,
  review_count INTEGER,
  best_seller_rank VARCHAR(255),
  listing_url VARCHAR(1000),
  bullets JSONB,
  aplus_summary TEXT,
  variants JSONB,
  confidence VARCHAR(50) NOT NULL DEFAULT 'low',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trend_snapshots (
  id SERIAL PRIMARY KEY,
  keyword_id INTEGER NOT NULL REFERENCES search_keywords(id),
  source VARCHAR(100) NOT NULL,
  window_days INTEGER NOT NULL,
  trend_score DOUBLE PRECISION NOT NULL,
  direction VARCHAR(50) NOT NULL,
  evidence_url VARCHAR(1000),
  summary TEXT,
  confidence VARCHAR(50) NOT NULL DEFAULT 'low',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS competitor_links (
  id SERIAL PRIMARY KEY,
  keyword_id INTEGER NOT NULL REFERENCES search_keywords(id),
  amazon_product_id INTEGER REFERENCES amazon_products(id),
  url VARCHAR(1000) NOT NULL,
  title VARCHAR(700),
  price DOUBLE PRECISION,
  rating DOUBLE PRECISION,
  review_count INTEGER,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS risk_assessments (
  id SERIAL PRIMARY KEY,
  keyword_id INTEGER NOT NULL REFERENCES search_keywords(id),
  infringement_risk VARCHAR(50) NOT NULL,
  patent_risk VARCHAR(50) NOT NULL,
  trademark_risk VARCHAR(50) NOT NULL,
  compliance_risk VARCHAR(50) NOT NULL,
  risk_score DOUBLE PRECISION NOT NULL,
  review_required BOOLEAN NOT NULL DEFAULT TRUE,
  rationale TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS profit_calculations (
  id SERIAL PRIMARY KEY,
  keyword_id INTEGER NOT NULL REFERENCES search_keywords(id),
  catalog_product_id INTEGER REFERENCES catalog_products(id),
  selling_price DOUBLE PRECISION NOT NULL,
  product_cost DOUBLE PRECISION,
  referral_fee DOUBLE PRECISION NOT NULL,
  fba_fee DOUBLE PRECISION NOT NULL,
  inbound_shipping DOUBLE PRECISION NOT NULL,
  ppc_buffer DOUBLE PRECISION NOT NULL,
  net_margin DOUBLE PRECISION NOT NULL,
  margin_rate DOUBLE PRECISION NOT NULL,
  confidence VARCHAR(50) NOT NULL DEFAULT 'estimated',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS source_evidence (
  id SERIAL PRIMARY KEY,
  entity_type VARCHAR(80) NOT NULL,
  entity_id INTEGER,
  source_name VARCHAR(120) NOT NULL,
  source_url VARCHAR(1000),
  captured_at TIMESTAMP NOT NULL DEFAULT NOW(),
  summary TEXT NOT NULL,
  confidence VARCHAR(50) NOT NULL DEFAULT 'low',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS opportunities (
  id SERIAL PRIMARY KEY,
  keyword_id INTEGER NOT NULL REFERENCES search_keywords(id),
  catalog_product_id INTEGER REFERENCES catalog_products(id),
  title VARCHAR(500) NOT NULL,
  category VARCHAR(255),
  target_audience TEXT,
  lifecycle_stage VARCHAR(80),
  seasonality VARCHAR(120),
  top_features JSONB,
  differentiation TEXT,
  demand_score DOUBLE PRECISION NOT NULL,
  margin_score DOUBLE PRECISION NOT NULL,
  competition_score DOUBLE PRECISION NOT NULL,
  catalog_match_score DOUBLE PRECISION NOT NULL,
  risk_score DOUBLE PRECISION NOT NULL,
  opportunity_score DOUBLE PRECISION NOT NULL,
  listing_difficulty VARCHAR(50) NOT NULL,
  risk_level VARCHAR(50) NOT NULL,
  recommended_action VARCHAR(80) NOT NULL,
  confidence VARCHAR(50) NOT NULL DEFAULT 'low',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_notes (
  id SERIAL PRIMARY KEY,
  opportunity_id INTEGER NOT NULL REFERENCES opportunities(id),
  user_id INTEGER NOT NULL REFERENCES users(id),
  body TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS saved_opportunities (
  id SERIAL PRIMARY KEY,
  opportunity_id INTEGER NOT NULL REFERENCES opportunities(id),
  user_id INTEGER NOT NULL REFERENCES users(id),
  status VARCHAR(50) NOT NULL DEFAULT 'watching',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE (opportunity_id, user_id)
);

CREATE TABLE IF NOT EXISTS sync_jobs (
  id SERIAL PRIMARY KEY,
  job_type VARCHAR(100) NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'queued',
  started_at TIMESTAMP,
  finished_at TIMESTAMP,
  payload JSONB,
  message TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  action VARCHAR(120) NOT NULL,
  entity_type VARCHAR(80),
  entity_id INTEGER,
  metadata_json JSONB,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_opportunities_score ON opportunities(opportunity_score DESC);
CREATE INDEX IF NOT EXISTS idx_risk_score ON risk_assessments(risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_source_evidence_entity ON source_evidence(entity_type, entity_id);
