# Architecture

```
+-----------------+        +-----------------------+
|   FastAPI API   | -----> |  Indexing Pipeline    |
| /v1/documents   |        |  (Parser + Builder)   |
+--------+--------+        +-----------+-----------+
         |                             |
         v                             v
+-----------------+        +-----------------------+
| Metadata Store  |        |  Artifact Store       |
| SQLite/Postgres |        |  JSON index artifacts |
+--------+--------+        +-----------+-----------+
         |                             |
         v                             v
+-----------------+        +-----------------------+
| Retriever       | <----- |  PageIndex Adapter    |
| BaselineTree    |        |  (swap-in ready)      |
+-----------------+        +-----------------------+
```

## Data flow

1. **Ingest**: upload a PDF/text → stored in metadata DB.
2. **Index**: background job parses pages/sections and writes index JSON.
3. **Query**: retrieval walks tree, returns citations + trace.

## Interfaces

- `VectorlessRetriever`: retrieval API used by the service.
- `ArtifactStore`: persistence for index JSON (local or S3).
- `MetadataStore`: document/job tracking (SQLite/Postgres).
