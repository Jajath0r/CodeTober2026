-- Jeu de données J18, identique à reference_history.csv du J17.
-- Tu peux aussi utiliser directement ta base catalog.db du J17.
CREATE TABLE IF NOT EXISTS catalog (
    product_id TEXT NOT NULL,
    name TEXT NOT NULL,
    unit_price_cents INTEGER NOT NULL,
    valid_from TEXT NOT NULL,
    valid_to TEXT,
    PRIMARY KEY (product_id, valid_from)
);
