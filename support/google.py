from google.cloud import storage
from datetime import timedelta

def generate_signed_url(bucket_name: str, blob_name: str):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(hours=1),
        method="GET"
    )
    return url

def generate_signed_urls(bucket_name, blob_prefix=""):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    blobs = list(bucket.list_blobs(prefix=blob_prefix))
    signed_urls = {}

    for blob in blobs:
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=15),
            method="GET"
        )
        signed_urls[blob.name] = url

    return signed_urls