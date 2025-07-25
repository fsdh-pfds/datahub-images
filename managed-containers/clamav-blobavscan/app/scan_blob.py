# pylint: disable=missing-module-docstring
import base64
import json
import os
import subprocess

from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueClient


def get_config():
    return {
        "storage_connection_string": os.getenv("storage_connection_string"),
        "queue_name": os.getenv("queue_name") or "virus-scan",
        "quarantine_container_name": os.getenv("quarantine_container_name") or "datahub-quarantine",
        "datahub_container_name": os.getenv("container_name") or "datahub",
    }

config = get_config()

queue_client = QueueClient.from_connection_string(
    conn_str=config["storage_connection_string"],
    queue_name=config["queue_name"],
)

blob_service_client = BlobServiceClient.from_connection_string(
    config["storage_connection_string"]
)




def scan_file(file_path):
    result = subprocess.run(
        ["clamscan", file_path],
        capture_output=True,
        text=True,
    )
    return "FOUND" in result.stdout


def process_message(message):
    json_data = json.loads(base64.b64decode(message.content))
    blob_url = json_data["data"]["blobUrl"]
    blob_name_full = json_data["subject"]
    blob_name_parts = blob_name_full.strip("/").split("/")
    blob_name_container = blob_name_parts[3]
    blob_name_in_container = "/".join(blob_name_parts[5:])
    print("processing blob: " + blob_name_full)

    if datahub_container_name.lower() != blob_name_container:
        print("skipping blob not in target container: " + blob_name_full)
        return

    # Download blob
    blob_client = blob_service_client.get_blob_client(
        container=datahub_container_name, blob=blob_name_in_container
    )
    local_path = "./blobfile"
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    if not blob_client.exists():
        print(f"Not foud: {blob_name_in_container} at {blob_url}")
        return

    with open(local_path, "wb") as f:
        f.write(blob_client.download_blob().readall())

    # Scan file (test file name please include "clamavtest2025a" )
    if scan_file(local_path) or "clamavtest2025a" in blob_name_in_container:
        print(f"Infected: {blob_name_in_container} at {blob_url}")

        # Set tag (Currently not working for storage accounts that
        # have hierarchical namespaces enabled. )
        # blob_client.set_blob_tags({"fsdh-scan-status": "failed"})

        # Move to infected container
        infected_blob_client = blob_service_client.get_blob_client(
            container=quarantine_container_name, blob=blob_name_in_container
        )
        with open(local_path, "rb") as data:
            infected_blob_client.upload_blob(data, overwrite=True)
        blob_client.delete_blob()
    else:
        print(f"Clean: {blob_name_in_container}")
        # blob_client.set_blob_tags({"fsdh-scan-status": "clean"})
        # Set tag (Currently not working for storage accounts that
        # have hierarchical namespaces enabled. )


def main():
    messages = queue_client.receive_messages(
        messages_per_page=10, visibility_timeout=14400
    )
    for msg_batch in messages.by_page():
        for msg in msg_batch:
            try:
                process_message(msg)
                queue_client.delete_message(msg)
            except Exception as e:
                print(f"Error processing message: {e}")


if __name__ == "__main__":
    main()
