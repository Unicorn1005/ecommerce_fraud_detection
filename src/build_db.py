import sqlite3
import pandas as pd

conn = sqlite3.connect("data/fraud.db")

for table, file in [("transactions", "train_transaction.csv"),
                    ("identity", "train_identity.csv")]:
    conn.execute(f"DROP TABLE IF EXISTS {table}")
    for chunk in pd.read_csv(f"data/raw/{file}", chunksize=50000):
        chunk.to_sql(table, conn, if_exists="append", index=False)
    print(table, "导入完成")

conn.commit()
conn.close()
