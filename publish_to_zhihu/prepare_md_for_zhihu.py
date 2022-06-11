import argparse
import os
import re

from convert_latex import convert_latex
from upload_image import upload_images

# IMAGE_LINK_RE = re.compile(
#     r"!\[[^\]]*\]\((?P<filename>.*?)(?=\"|\))(?P<optionalpart>\".*\")?\)"
# )
CONN_STR_RE = re.compile("AccountName=(.*?);.*EndpointSuffix=(.*?)($|;)")


def get_azure_blob_url(conn_str):
    m = CONN_STR_RE.search(conn_str)
    return f"https://{m.group(1)}.blob.{m.group(2)}"


OBSIDIAN_IMAGE_LINK_RE = re.compile(r"!\[\[([^\]]*)\]\]")


parser = argparse.ArgumentParser(
    description="""
Convert standard Markdown file to Zhihu Format
1. Convert latex formula
2. Upload all the images

Assume all the local image links in markdown file is relative paths based on `image_folder`
"""
)

parser.add_argument(
    "--container",
    help="The Container which the file will be uploaded to.",
    default="imagehost",
)
parser.add_argument("image_link_root", help="The root folder of image links.")
parser.add_argument("output_folder", help="The folder to store converted md files")
parser.add_argument(
    "files", nargs="+", help="The file to be uploaded. Must Include at least one."
)

args = parser.parse_args()
container = args.container
image_link_root = args.image_link_root
output_folder = args.output_folder
files = args.files
conn_str = os.environ["IMAGEHOST_CONN_STR"]
azure_blob_url = get_azure_blob_url(conn_str)


def process_image_link(azure_blob_url, container, conn_str, image_folder, re_match):
    image_link = re_match.group(1)
    if not image_link.startswith("http://") and not image_link.startswith("https://"):
        uploaded_urls = upload_images(
            azure_blob_url,
            container,
            conn_str,
            image_folder,
            [image_link],
            overwrite=True,
        )
        image_link = uploaded_urls[0]
    return f'<img src="{image_link}" class="origin_image zh-lightbox-thumb lazy">\n'


os.makedirs(output_folder, exist_ok=True)

for file_path in files:
    output_file_path = os.path.join(output_folder, os.path.split(file_path)[1])
    with open(file_path, encoding="utf-8") as in_f, open(
        output_file_path, "w", encoding="utf-8"
    ) as out_f:
        content = in_f.read()
        new_content = OBSIDIAN_IMAGE_LINK_RE.sub(
            lambda m: process_image_link(
                azure_blob_url, container, conn_str, image_link_root, m
            ),
            content,
        )
        new_content = convert_latex(new_content)
        out_f.write(new_content)
