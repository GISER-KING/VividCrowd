import sqlite3
import os

# 数据库路径
db_path = os.path.join("backend", "data", "digital_customer.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("检查 customer_chunks 表的外键约束")
print("=" * 60)

# 检查外键约束
cursor.execute("PRAGMA foreign_key_list(customer_chunks)")
fks = cursor.fetchall()

if fks:
    print(f"找到 {len(fks)} 个外键约束：")
    for fk in fks:
        print(f"  - 表: {fk[2]}, 列: {fk[3]} -> {fk[4]}, ON DELETE: {fk[5]}")
else:
    print("⚠️ 没有找到外键约束！")

print("\n" + "=" * 60)
print("检查 PRAGMA foreign_keys 设置")
print("=" * 60)

cursor.execute("PRAGMA foreign_keys")
fk_enabled = cursor.fetchone()[0]
print(f"Foreign keys enabled: {fk_enabled}")

conn.close()
