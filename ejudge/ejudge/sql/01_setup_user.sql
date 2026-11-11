-- Run as a DBA (SYS / ADMIN) once.
-- Creates the schema that owns the eJudge objects.

CREATE USER ejudge IDENTIFIED BY "ChangeMe_#123"
  DEFAULT TABLESPACE users QUOTA UNLIMITED ON users;

GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE SEQUENCE,
      CREATE PROCEDURE, CREATE MINING MODEL TO ejudge;

-- Needed for DBMS_VECTOR / DBMS_VECTOR_CHAIN
GRANT DB_DEVELOPER_ROLE TO ejudge;

-- OPTIONAL: only if you load the ONNX file from a server directory
-- (not needed when using python/load_model.py, which uploads it as a BLOB)
-- CREATE OR REPLACE DIRECTORY model_dir AS '/opt/oracle/models';
-- GRANT READ, WRITE ON DIRECTORY model_dir TO ejudge;
