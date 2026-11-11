"""
Load the ONNX embedding model into the database (slide 6, step 2).

Uploads the file as a BLOB, so no server-side DIRECTORY is required.

Usage:  python load_model.py models/all_MiniLM_L6_v2.onnx
"""
import sys
from pathlib import Path

import oracledb

from config import get_connection

MODEL_NAME = "ALL_MINILM_L6_V2"

path = Path(sys.argv[1] if len(sys.argv) > 1 else "models/all_MiniLM_L6_v2.onnx")
data = path.read_bytes()

conn = get_connection()
cur = conn.cursor()

# Drop any previous version
cur.execute(
    "SELECT COUNT(*) FROM user_mining_models WHERE model_name = :n", n=MODEL_NAME
)
if cur.fetchone()[0]:
    cur.execute("BEGIN DBMS_VECTOR.DROP_ONNX_MODEL(:n, TRUE); END;", n=MODEL_NAME)

cur.setinputsizes(blob=oracledb.DB_TYPE_BLOB)
cur.execute(
    """
    BEGIN
      DBMS_VECTOR.LOAD_ONNX_MODEL(
        model_name => :name,
        model_data => :blob,
        metadata   => JSON('{"function":"embedding",
                             "embeddingOutput":"embedding",
                             "input":{"input":["DATA"]}}'));
    END;""",
    name=MODEL_NAME,
    blob=data,
)

# Sanity check: should print 384
cur.execute(
    f"SELECT VECTOR_DIMS_COUNT(VECTOR_EMBEDDING({MODEL_NAME} USING 'hello' AS data)) FROM dual"
)
print(f"Model {MODEL_NAME} loaded. Embedding dimensions: {cur.fetchone()[0]}")
conn.close()
