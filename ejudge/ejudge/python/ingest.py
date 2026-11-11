"""
Load judgment PDFs / Word files into the DB and vectorize them.

Usage:  python ingest.py judgements/            (a folder)
        python ingest.py judgements/case1.pdf   (one file)
"""
import sys
from pathlib import Path

import oracledb

from config import get_connection

EXTS = {".pdf", ".docx", ".doc"}


def files_from(arg: str):
    p = Path(arg)
    if p.is_file():
        yield p
    else:
        yield from (f for f in sorted(p.rglob("*")) if f.suffix.lower() in EXTS)


def main(target: str):
    conn = get_connection()
    cur = conn.cursor()

    for f in files_from(target):
        cur.execute("SELECT doc_id FROM judgements WHERE file_name = :n", n=f.name)
        row = cur.fetchone()

        if row:
            doc_id = row[0]
            print(f"[skip upload] {f.name} already stored (doc_id={doc_id})")
        else:
            doc_id_var = cur.var(int)
            cur.setinputsizes(blob=oracledb.DB_TYPE_BLOB)
            cur.execute(
                """INSERT INTO judgements (file_name, file_blob)
                   VALUES (:name, :blob) RETURNING doc_id INTO :id""",
                name=f.name,
                blob=f.read_bytes(),
                id=doc_id_var,
            )
            doc_id = doc_id_var.getvalue()[0]
            conn.commit()
            print(f"[uploaded]    {f.name} (doc_id={doc_id})")

        cur.callproc("vectorize_judgement", [doc_id])
        cur.execute(
            "SELECT COUNT(*) FROM judgement_chunks WHERE doc_id = :d", d=doc_id
        )
        print(f"[vectorized]  {cur.fetchone()[0]} chunks")

    conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
