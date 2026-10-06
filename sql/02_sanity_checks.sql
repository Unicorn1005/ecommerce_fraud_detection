-- 建库后的基础核对查询（可在 DB Browser for SQLite 或 sqlite3 命令行中运行）

-- 1. 两张表的行数
SELECT 'transactions' AS table_name, COUNT(*) AS n_rows FROM transactions
UNION ALL
SELECT 'identity', COUNT(*) FROM identity;

-- 2. 整体欺诈率
SELECT COUNT(*) AS n_tx,
       SUM(isFraud) AS n_fraud,
       ROUND(100.0 * SUM(isFraud) / COUNT(*), 2) AS fraud_rate_pct
FROM transactions;

-- 3. 身份表覆盖率：有多少交易能关联到身份信息
SELECT COUNT(*) AS n_tx_with_identity,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM transactions), 1) AS coverage_pct
FROM transactions t
JOIN identity i ON t.TransactionID = i.TransactionID;

-- 4. 按产品类型的欺诈率（第 2 天分析的起点）
SELECT ProductCD,
       COUNT(*) AS n_tx,
       SUM(isFraud) AS n_fraud,
       ROUND(100.0 * SUM(isFraud) / COUNT(*), 2) AS fraud_rate_pct
FROM transactions
GROUP BY ProductCD
ORDER BY fraud_rate_pct DESC;
