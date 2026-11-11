-- Run as EJUDGE after the model is loaded (python/load_model.py) and
-- at least one row exists in JUDGEMENTS (python/ingest.py).

-- 1) BLOB -> text -> chunks -> embeddings -> table  (slide 6, steps 1 & 3)
--    Re-runnable for a single document by passing its DOC_ID.
CREATE OR REPLACE PROCEDURE vectorize_judgement(p_doc_id IN NUMBER) AS
BEGIN
  DELETE FROM judgement_chunks WHERE doc_id = p_doc_id;

  INSERT INTO judgement_chunks (doc_id, chunk_id, chunk_text, embed_vector)
  SELECT j.doc_id,
         et.embed_id,
         et.embed_data,
         TO_VECTOR(et.embed_vector)
  FROM   judgements j,
         dbms_vector_chain.utl_to_embeddings(
           dbms_vector_chain.utl_to_chunks(
             dbms_vector_chain.utl_to_text(j.file_blob),
             JSON('{"by":"words","max":"200","overlap":"20",
                    "split":"recursively","normalize":"all"}')),
           JSON('{"provider":"database","model":"ALL_MINILM_L6_V2"}')
         ) t,
         JSON_TABLE(t.column_value, '$'
           COLUMNS (embed_id     NUMBER         PATH '$.embed_id',
                    embed_data   VARCHAR2(4000) PATH '$.embed_data',
                    embed_vector CLOB           PATH '$.embed_vector')) et
  WHERE  j.doc_id = p_doc_id;

  COMMIT;
END;
/

-- 2) Similarity search  (slide 6, steps 4 & 5)
--    Returns the best chunk per judgment, closest first.
CREATE OR REPLACE FUNCTION judge_search(
  p_query IN VARCHAR2,
  p_top   IN NUMBER DEFAULT 5
) RETURN SYS_REFCURSOR AS
  l_qv  VECTOR;
  l_rc  SYS_REFCURSOR;
BEGIN
  l_qv := VECTOR_EMBEDDING(ALL_MINILM_L6_V2 USING p_query AS data);

  OPEN l_rc FOR
    SELECT j.file_name,
           c.chunk_id,
           c.chunk_text,
           VECTOR_DISTANCE(c.embed_vector, l_qv, EUCLIDEAN_SQUARED) AS distance
    FROM   judgement_chunks c
    JOIN   judgements j ON j.doc_id = c.doc_id
    ORDER  BY distance
    FETCH APPROX FIRST p_top ROWS ONLY WITH TARGET ACCURACY 60;

  RETURN l_rc;
END;
/

-- Quick test in SQL Developer / VS Code SQL extension:
-- DECLARE rc SYS_REFCURSOR; BEGIN rc := judge_search('impugned judgement', 5); DBMS_SQL.RETURN_RESULT(rc); END;
-- /
