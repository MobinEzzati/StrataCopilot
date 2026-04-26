import boto3
from botocore.exceptions import ClientError
from app.core.settings.Setting import settings

class S3Repository:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        self.bucket = settings.s3_bucket_name

    def upload(self, file_obj, key: str, content_type: str):
        self.client.upload_fileobj(
            file_obj, self.bucket, key,
            ExtraArgs={"ContentType": content_type}
        )

    def delete(self, key: str):
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def generate_presigned_url(self, key: str, expiry: int) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expiry,
        )

    def list_objects(self, prefix: str = "") -> list:
        response = self.client.list_objects_v2(
            Bucket=self.bucket, Prefix=prefix
        )
        return [obj["Key"] for obj in response.get("Contents", [])]
