#!/usr/local/bin/python3
# author: timkhuang

import argparse
import os
import re

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient, PublicAccess

name_regex = re.compile("[^a-z0-9]")  # Make sure container name follows the azure rule.


def upload(
    storage_account_url, container_name, connection_string, file_root, file_collection
):
    if not storage_account_url.endswith("/"):
        storage_account_url += "/"
    # Create container if not exist.
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    try:
        container = blob_service_client.create_container(container_name)
        container.set_container_access_policy({}, public_access=PublicAccess.Blob)
    except ResourceExistsError:
        pass

    # Upload
    uploaded_urls = []
    for file_rel_path in file_collection:
        file_type = file_rel_path.split(".")[-1]
        # blob_name = (
        #     name_regex.sub("-", file_rel_path.split("/")[-1].lower()) + "." + file_type
        # )
        blob_name = file_rel_path.replace("\\", "/")
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=blob_name
        )
        with open(os.path.join(file_root, file_rel_path), "rb") as data:
            blob_client.upload_blob(data)
        uploaded_urls.append(storage_account_url + container_name + "/" + blob_name)
    return uploaded_urls


if __name__ == "__main__":
    # Parse commandline arguments
    parser = argparse.ArgumentParser(
        description="Upload image to the Azure Image Host."
    )
    parser.add_argument(
        "-u",
        "--url",
        help="The public url to access the resources and the final url will be print.(Account Level)",
    )
    parser.add_argument(
        "Container", help="The Container which the file will be uploaded to."
    )
    parser.add_argument("ConnStr", help="The Azure Storage Account Connect String.")
    parser.add_argument("FileRoot", help="The root folder of files to be uploaded")
    parser.add_argument(
        "File", nargs="+", help="The file to be uploaded. Must Include at least one."
    )
    args = vars(parser.parse_args())

    url = args["url"]
    container_name = name_regex.sub("-", args["Container"].lower())
    connection_string = args["ConnStr"]
    file_root = args["FileRoot"]
    file_collection = args["File"]
    uploaded_urls = upload(
        url, container_name, connection_string, file_root, file_collection
    )
    for uploaded_url in uploaded_urls:
        print(uploaded_url)
