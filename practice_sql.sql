SELECT current_database();

DROP alembic_version;

DELETE FROM alembic_version;

SELECT id, title , doc_metadata from documents;

SELECT count(*) FROM document_chunks;