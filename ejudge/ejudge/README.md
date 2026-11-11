# eJudge – Precedence of Precedent (Oracle 23ai AI Vector Search)

Finds earlier judgments similar to a query by embedding judgment text with an
ONNX model inside Oracle 23ai and ranking chunks by `EUCLIDEAN_SQUARED`
distance (target accuracy 60).

```
PDF/Word ──► BLOB in 23ai ──► utl_to_text ─► utl_to_chunks ─► utl_to_embeddings ─► VECTOR column
                                                                         │
 query text ─► VECTOR_EMBEDDING ─► VECTOR_DISTANCE (EUCLIDEAN_SQUARED) ─┘ ─► results (CLI / APEX)
```

## Prerequisites
- Oracle Database 23ai (Free container works: `container-registry.oracle.com/database/free`)
- Python 3.10+
- An ONNX embedding model with tokenizer, e.g. all-MiniLM-L6-v2
  (build with `python/export_model.py`, or use Oracle's pre-built augmented ONNX)

## Setup in VS Code
1. Install the **Oracle SQL Developer Extension for VS Code** (to run the .sql files) and **Python**.
2. Python env:
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env             # then edit credentials / DSN
   ```
3. Run SQL as a DBA: `sql/01_setup_user.sql`
4. Run as `EJUDGE`: `sql/02_tables.sql`, then `sql/03_ingest_and_search.sql`
5. Load the model:
   ```bash
   python python/load_model.py models/all_MiniLM_L6_v2.onnx
   ```
6. Put judgments in `judgements/` and ingest:
   ```bash
   python python/ingest.py judgements/
   ```
7. Search:
   ```bash
   python python/search.py "impugned judgement" --top 5
   ```
8. (Optional) Build the APEX UI: see `apex/apex_page_setup.md`.

## Notes
- The vector index is IVF (`NEIGHBOR PARTITIONS`); create it after loading some data
  for better partitioning, or recreate it later.
- If `utl_to_text` fails on a file, it is usually a scanned (image-only) PDF; OCR it first.
- Chunking is 200 words with 20 overlap; tune in `vectorize_judgement`.
- Slide 3 mentions OCI Object Storage for the files; this version stores them as BLOBs in the DB.
