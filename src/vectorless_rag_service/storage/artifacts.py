from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import boto3

from vectorless_rag_service.config import settings
from vectorless_rag_service.core.interfaces import ArtifactStore
from vectorless_rag_service.core.models import IndexArtifact


class LocalArtifactStore(ArtifactStore):
    def __init__(self, base_path: str) -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _path(self, document_id: UUID) -> Path:
        return self.base_path / f"{document_id}.json"

    def put(self, document_id: UUID, artifact: IndexArtifact) -> str:
        path = self._path(document_id)
        path.write_text(artifact.model_dump_json(indent=2))
        return str(path)

    def get(self, document_id: UUID) -> IndexArtifact:
        path = self._path(document_id)
        data = json.loads(path.read_text())
        return IndexArtifact.model_validate(data)

    def exists(self, document_id: UUID) -> bool:
        return self._path(document_id).exists()


class S3ArtifactStore(ArtifactStore):
    def __init__(self, bucket: str, endpoint: str | None) -> None:
        self.bucket = bucket
        self.client = boto3.client("s3", endpoint_url=endpoint)

    def _key(self, document_id: UUID) -> str:
        return f"artifacts/{document_id}.json"

    def put(self, document_id: UUID, artifact: IndexArtifact) -> str:
        payload = artifact.model_dump_json(indent=2)
        key = self._key(document_id)
        self.client.put_object(Bucket=self.bucket, Key=key, Body=payload.encode("utf-8"))
        return f"s3://{self.bucket}/{key}"

    def get(self, document_id: UUID) -> IndexArtifact:
        key = self._key(document_id)
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        data = json.loads(response["Body"].read().decode("utf-8"))
        return IndexArtifact.model_validate(data)

    def exists(self, document_id: UUID) -> bool:
        key = self._key(document_id)
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False


def build_artifact_store() -> ArtifactStore:
    if settings.storage.provider == "s3":
        if settings.storage.s3_bucket is None:
            raise ValueError("S3 bucket must be set")
        return S3ArtifactStore(settings.storage.s3_bucket, settings.storage.s3_endpoint)
    return LocalArtifactStore(settings.storage.local_path)
