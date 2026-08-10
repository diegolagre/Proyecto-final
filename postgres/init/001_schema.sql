CREATE SCHEMA IF NOT EXISTS dwh;

CREATE TABLE IF NOT EXISTS dwh.dim_company_code (
    company_code_key BIGSERIAL PRIMARY KEY,
    company_code VARCHAR(4) NOT NULL UNIQUE,
    company_name VARCHAR(120) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dwh.dim_profit_center (
    profit_center_key BIGSERIAL PRIMARY KEY,
    profit_center VARCHAR(10) NOT NULL UNIQUE,
    description VARCHAR(120),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dwh.fact_copa (
    copa_key BIGSERIAL PRIMARY KEY,
    document_number VARCHAR(20) NOT NULL,
    fiscal_year SMALLINT NOT NULL,
    fiscal_period SMALLINT NOT NULL CHECK (fiscal_period BETWEEN 1 AND 16),
    company_code_key BIGINT NOT NULL REFERENCES dwh.dim_company_code(company_code_key),
    profit_center_key BIGINT REFERENCES dwh.dim_profit_center(profit_center_key),
    revenue NUMERIC(18, 2) NOT NULL DEFAULT 0,
    cost NUMERIC(18, 2) NOT NULL DEFAULT 0,
    currency CHAR(3) NOT NULL,
    source_updated_at TIMESTAMPTZ,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (document_number, fiscal_year, fiscal_period, company_code_key)
);

CREATE INDEX IF NOT EXISTS idx_fact_copa_period
    ON dwh.fact_copa (fiscal_year, fiscal_period);

CREATE INDEX IF NOT EXISTS idx_fact_copa_profit_center
    ON dwh.fact_copa (profit_center_key);
