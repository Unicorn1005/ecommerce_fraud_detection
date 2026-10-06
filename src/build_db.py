"""把 IEEE-CIS 的两张 CSV 导入 SQLite，并建立索引和关联视图。

用法（在仓库根目录运行）:
    python src/build_db.py
    python src/build_db.py --data-dir data/raw --db data/fraud.db --chunksize 50000

产出:
    data/fraud.db 中的表 transactions、identity，以及视图 v_transactions
    （交易表 LEFT JOIN 身份表，保留所有交易，没有身份信息的交易相关列为 NULL）
"""
import argparse
import sqlite3
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

FILES = {
    "transactions": "train_transaction.csv",
    "identity": "train_identity.csv",
}


def load_csv(conn, csv_path, table, chunksize):
    """分块读取 CSV 并写入 SQLite，避免一次性占用过多内存。"""
    conn.execute(f"DROP TABLE IF EXISTS {table}")
    total = 0
    start = time.time()
    for chunk in pd.read_csv(csv_path, chunksize=chunksize):
        chunk.to_sql(table, conn, if_exists="append", index=False)
        total += len(chunk)
        print(f"  {table}: 已导入 {total:,} 行 ({time.time() - start:.0f}s)", flush=True)
    conn.commit()
    return total


def create_view(conn):
    """动态生成视图：交易表全部列 + 身份表中除 TransactionID 外的列。"""
    id_cols = [
        row[1]
        for row in conn.execute("PRAGMA table_info(identity)")
        if row[1] != "TransactionID"
    ]
    select_id = ", ".join(f'i."{c}"' for c in id_cols)
    conn.execute("DROP VIEW IF EXISTS v_transactions")
    conn.execute(
        f"""
        CREATE VIEW v_transactions AS
        SELECT t.*, {select_id}
        FROM transactions t
        LEFT JOIN identity i ON t.TransactionID = i.TransactionID
        """
    )
    conn.commit()


def run_sql_file(conn, path):
    conn.executescript(Path(path).read_text(encoding="utf-8"))
    conn.commit()


def verify(conn):
    """简单核对：行数、欺诈率、身份表覆盖率。"""
    n_tx = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    n_id = conn.execute("SELECT COUNT(*) FROM identity").fetchone()[0]
    n_view = conn.execute("SELECT COUNT(*) FROM v_transactions").fetchone()[0]
    fraud = conn.execute("SELECT AVG(isFraud) FROM transactions").fetchone()[0]
    matched = conn.execute(
        "SELECT COUNT(*) FROM transactions t JOIN identity i USING (TransactionID)"
    ).fetchone()[0]
    print("\n== 核对结果 ==")
    print(f"交易表行数:       {n_tx:,}")
    print(f"身份表行数:       {n_id:,}")
    print(f"视图行数:         {n_view:,}  (应等于交易表行数: {n_view == n_tx})")
    print(f"整体欺诈率:       {fraud:.2%}")
    print(f"有身份信息的交易: {matched:,} ({matched / n_tx:.1%})")


def main():
    parser = argparse.ArgumentParser(description="构建 IEEE-CIS 的 SQLite 数据库")
    parser.add_argument("--data-dir", default=str(ROOT / "data" / "raw"))
    parser.add_argument("--db", default=str(ROOT / "data" / "fraud.db"))
    parser.add_argument("--chunksize", type=int, default=50000)
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    missing = [f for f in FILES.values() if not (data_dir / f).exists()]
    if missing:
        raise SystemExit(f"在 {data_dir} 中找不到: {', '.join(missing)}。请先下载数据。")

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        for table, filename in FILES.items():
            print(f"导入 {filename} -> 表 {table}")
            load_csv(conn, data_dir / filename, table, args.chunksize)
        print("建立索引...")
        run_sql_file(conn, ROOT / "sql" / "01_indexes.sql")
        print("建立关联视图...")
        create_view(conn)
        verify(conn)
    finally:
        conn.close()
    print(f"\n完成，数据库文件: {db_path}")


if __name__ == "__main__":
    main()
