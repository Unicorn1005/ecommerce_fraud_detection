-- 为常用的关联和分组字段建立索引，加快后面的聚合查询
CREATE INDEX IF NOT EXISTS idx_tx_id ON transactions (TransactionID);
CREATE INDEX IF NOT EXISTS idx_tx_fraud ON transactions (isFraud);
CREATE INDEX IF NOT EXISTS idx_tx_product ON transactions (ProductCD);
CREATE INDEX IF NOT EXISTS idx_tx_dt ON transactions (TransactionDT);
CREATE INDEX IF NOT EXISTS idx_id_id ON identity (TransactionID);
