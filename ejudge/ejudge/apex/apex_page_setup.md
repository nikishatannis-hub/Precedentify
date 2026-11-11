# APEX page (matches the "judgement search" screenshot, slide 7)

Create an APEX app **judgement search** with a blank page **JUDGE_PAGE**.

## Items / buttons
| Component | Name | Notes |
|---|---|---|
| Text Field | `P1_INPUT` | label "Input" |
| Button | `SUBMIT` | action: Submit Page |

## Region: "Response" (Classic Report, SQL Query)

```sql
SELECT j.file_name,
       c.chunk_text AS response,
       ROUND(VECTOR_DISTANCE(
               c.embed_vector,
               VECTOR_EMBEDDING(ALL_MINILM_L6_V2 USING :P1_INPUT AS data),
               EUCLIDEAN_SQUARED), 4) AS distance
FROM   judgement_chunks c
JOIN   judgements j ON j.doc_id = c.doc_id
WHERE  :P1_INPUT IS NOT NULL
ORDER  BY distance
FETCH APPROX FIRST 5 ROWS ONLY WITH TARGET ACCURACY 60
```

Set the region's **Page Items to Submit** = `P1_INPUT`, and make the region
server-side conditional on `P1_INPUT IS NOT NULL`.

The parsing schema of the APEX workspace must be `EJUDGE` (or have SELECT on
the tables and EXECUTE on the model).
