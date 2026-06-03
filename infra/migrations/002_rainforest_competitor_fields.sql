ALTER TABLE amazon_products
ADD COLUMN IF NOT EXISTS estimated_monthly_sales DOUBLE PRECISION,
ADD COLUMN IF NOT EXISTS image_url VARCHAR(1000),
ADD COLUMN IF NOT EXISTS lifecycle_stage VARCHAR(80),
ADD COLUMN IF NOT EXISTS feature_tags JSONB,
ADD COLUMN IF NOT EXISTS data_source VARCHAR(120);

ALTER TABLE competitor_links
ADD COLUMN IF NOT EXISTS asin VARCHAR(30),
ADD COLUMN IF NOT EXISTS estimated_monthly_sales DOUBLE PRECISION,
ADD COLUMN IF NOT EXISTS image_url VARCHAR(1000),
ADD COLUMN IF NOT EXISTS differentiation TEXT;

CREATE INDEX IF NOT EXISTS idx_competitor_links_keyword ON competitor_links(keyword_id);
CREATE INDEX IF NOT EXISTS idx_amazon_products_asin ON amazon_products(asin);
