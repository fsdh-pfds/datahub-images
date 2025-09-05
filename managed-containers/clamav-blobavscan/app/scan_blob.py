# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=import-error

import base64
import io
import json
import os
import tempfile

import pyclamd
from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueClient

CHUNK_SIZE = 1024 * 1024 * 1024 * 1


def get_config():
    return {
        "storage_connection_string": os.getenv("storage_connection_string"),
        "queue_name": os.getenv("queue_name") or "virus-scan",
        "quarantine_container_name": os.getenv("quarantine_container_name") or "datahub-quarantine",
        "datahub_container_name": os.getenv("container_name") or "datahub",
        "WORK_DIR": os.getenv("WORK_DIR") or "/datahub-temp",
    }


config = get_config()

queue_client = QueueClient.from_connection_string(
    conn_str=config["storage_connection_string"],
    queue_name=config["queue_name"],
)

blob_service_client = BlobServiceClient.from_connection_string(config["storage_connection_string"])

def process_message(message):
    json_data = json.loads(base64.b64decode(message.content))
    blob_url = json_data["data"]["blobUrl"]
    blob_name_full = json_data["subject"]
    blob_name_parts = blob_name_full.strip("/").split("/")
    blob_name_container = blob_name_parts[3]
    blob_name_in_container = "/".join(blob_name_parts[5:])
    print("FSDH - processing blob: " + blob_name_full)

    if config["datahub_container_name"].lower() != blob_name_container:
        print("FSDH - skipping blob not in target container: " + blob_name_full)
        return

    blob_client = blob_service_client.get_blob_client(
        container=config["datahub_container_name"], blob=blob_name_in_container
    )

    if not blob_client.exists():
        print(f"FSDH - blob Not foud: {blob_name_in_container} at {blob_url}")
        return

    blob_properties = blob_client.get_blob_properties()
    blob_size = blob_properties.size
    blob_metadata = blob_properties.metadata
    chunk_start = 0
    chunk_index = 0
    file_infected = 0

    while chunk_start < blob_size:
        chunk_end = min(chunk_start + CHUNK_SIZE, blob_size) - 1
        print(f"FSDH - Downloading chunk {chunk_index} to tempfile: bytes {chunk_start} to {chunk_end}")


        clamav_socket = pyclamd.ClamdUnixSocket()
        with tempfile.NamedTemporaryFile(delete=True, suffix="filechunk") as temp_file:
            print("FSDH - chunk scan as tempfile: " + blob_name_full + f" chunk {chunk_index} tempfile {temp_file.name}")
            with open(temp_file.name, "wb") as file:
                file.write(blob_client.download_blob(offset=chunk_start, length=chunk_end - chunk_start + 1).readall())
                os.chmod(temp_file.name, 0o666)


            print("FSDH - temp file: ", os.path.getsize(temp_file.name),  " readable ", os.access(temp_file.name, os.R_OK))
            result = clamav_socket.scan_file(temp_file.name)
            print("FSDH - chunk scan completed: " + blob_name_full + f" chunk {chunk_index}")

            threat_found = 0
            if result is None:
                print("FSDH - scan result None: " + blob_name_full + f" chunk {chunk_index}")
            else:
                for fname, (status, virus) in result.items():
                    if status == 'FOUND':
                        threat_found += 1
                        print("FSDH - chunk result FOUND: " + blob_name_full + f" chunk {chunk_index} {virus}")
                    elif status == 'OK':
                        print("FSDH - chunk result OK: " + blob_name_full + f" chunk {chunk_index}")
                    else:
                        print("FSDH - chunk result " + status + virus)

            if ( threat_found > 0 ) or "clamavtest2025a" in blob_name_in_container:
                blob_client.delete_blob()
                print(f"FSDH - Infected blob chunk {chunk_index}: {blob_name_in_container} at {blob_url}: {virus}")

                # Create marker in infected container
                infected_blob_client = blob_service_client.get_blob_client(
                    container=config["quarantine_container_name"],
                    blob=blob_name_in_container,
                )
                infected_blob_client.upload_blob(
                    io.BytesIO(
                        "This file was removed by FSDH due to potential threat | "
                        "Ce fichier a été supprimé par PFDS en raison d'une menace potentielle. ".encode("utf-8")
                    ),
                    overwrite=True,
                )

                file_infected += 1
                break
            else:
                print(f"FSDH - blob chunk {chunk_index} is clean: {blob_name_in_container}")

        chunk_start += CHUNK_SIZE
        chunk_index += 1
    
    if file_infected < 1 :
        more_blob_metadata = {'avscan': 'ok'}
        blob_metadata.update(more_blob_metadata)
        blob_client.set_blob_metadata(metadata=blob_metadata)


def main():
    messages = queue_client.receive_messages(messages_per_page=10, visibility_timeout=14400)
    for msg_batch in messages.by_page():
        for msg in msg_batch:
            try:
                process_message(msg)
                queue_client.delete_message(msg)
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"FSDH - Error processing message: {e}")


if __name__ == "__main__":
    main()
