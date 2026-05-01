"""MinIO file storage service shared across microservices."""
import io
import json
from typing import Optional
from minio import Minio
from minio.error import S3Error
from common.config import ServiceSettings


class StorageService:
    """S3-compatible object storage for receipt images and exports."""

    def __init__(self, endpoint: str = "", access_key: str = "", secret_key: str = "", bucket: str = ""):
        settings = ServiceSettings()
        self.client = Minio(
            endpoint or settings.MINIO_ENDPOINT,
            access_key=access_key or settings.MINIO_ACCESS_KEY,
            secret_key=secret_key or settings.MINIO_SECRET_KEY,
            secure=False,
        )
        self.bucket = bucket or settings.MINIO_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self):
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
            # Make bucket publicly readable for image serving via gateway
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject"],
                        "Resource": f"arn:aws:s3:::{self.bucket}/*",
                    }
                ],
            }
            self.client.set_bucket_policy(self.bucket, json.dumps(policy))

    def upload_file(self, file_data: bytes, filename: str, content_type: str = "image/jpeg") -> str:
        """Upload a file to MinIO and return the public URL."""
        self.client.put_object(
            self.bucket,
            filename,
            io.BytesIO(file_data),
            length=len(file_data),
            content_type=content_type,
        )
        return f"/api/storage/{filename}"

    def get_file(self, filename: str) -> Optional[bytes]:
        """Retrieve a file from MinIO."""
        try:
            response = self.client.get_object(self.bucket, filename)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error:
            return None

    def delete_file(self, filename: str) -> bool:
        """Delete a file from MinIO."""
        try:
            self.client.remove_object(self.bucket, filename)
            return True
        except S3Error:
            return False

    def list_files(self, prefix: str = "") -> list:
        """List files with optional prefix."""
        objects = self.client.list_objects(self.bucket, prefix=prefix, recursive=True)
        return [obj.object_name for obj in objects]


# Lazy singleton
_storage_instance: Optional[StorageService] = None


def get_storage() -> StorageService:
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = StorageService()
    return _storage_instance
