-- Run as EJUDGE.

-- One row per judgment file (PDF / Word) stored as a BLOB
CREATE TABLE judgements (
  doc_id      NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  file_name   VARCHAR2(400) NOT NULL UNIQUE,
  file_blob   BLOB          NOT NULL,
  uploaded_at TIMESTAMP DEFAULT SYSTIMESTAMP
);

-- One row per text chunk, with its embedding
-- MiniLM-L6-v2 produces 384-dimension vectors
CREATE TABLE judgement_chunks (
  doc_id       NUMBER NOT NULL REFERENCES judgements(doc_id) ON DELETE CASCADE,
  chunk_id     NUMBER NOT NULL,
  chunk_text   VARCHAR2(4000),
  embed_vector VECTOR(384, FLOAT32),
  CONSTRAINT judgement_chunks_pk PRIMARY KEY (doc_id, chunk_id)
);

-- Approximate (IVF) vector index. Metric + target accuracy match the slides.
CREATE VECTOR INDEX judgement_chunks_vidx
  ON judgement_chunks (embed_vector)
  ORGANIZATION NEIGHBOR PARTITIONS
  DISTANCE EUCLIDEAN_SQUARED
  WITH TARGET ACCURACY 60;
