"""
eJudge command-line search.

Usage:  python search.py "impugned judgement"
        python search.py "bail in cheque bounce case" --top 10
"""
import argparse
import textwrap

from config import get_connection

SQL = """
SELECT j.file_name,
       c.chunk_id,
       c.chunk_text,
       VECTOR_DISTANCE(c.embed_vector,
                       VECTOR_EMBEDDING(ALL_MINILM_L6_V2 USING :q AS data),
                       EUCLIDEAN_SQUARED) AS distance
FROM   judgement_chunks c
JOIN   judgements j ON j.doc_id = c.doc_id
ORDER  BY distance
FETCH APPROX FIRST :top ROWS ONLY WITH TARGET ACCURACY 60
"""


def search(query: str, top: int = 5):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(SQL, q=query, top=top)
        return cur.fetchall()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--top", type=int, default=5)
    args = ap.parse_args()

    for rank, (name, chunk_id, text, dist) in enumerate(
        search(args.query, args.top), 1
    ):
        print(f"\n#{rank}  {name}  (chunk {chunk_id})  distance={dist:.4f}")
        print(textwrap.indent(textwrap.fill((text or "")[:600], 90), "    "))
