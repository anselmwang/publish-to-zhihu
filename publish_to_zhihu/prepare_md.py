import argparse
import os
import re

from .convert_latex import convert_latex
from .upload_images import upload_images

# IMAGE_LINK_RE = re.compile(
#     r"!\[[^\]]*\]\((?P<filename>.*?)(?=\"|\))(?P<optionalpart>\".*\")?\)"
# )


OBSIDIAN_IMAGE_LINK_RE = re.compile(r"!\[\[([^\]]*)\]\]")

def process_image_link(container, conn_str, image_folder, re_match):
    image_link = re_match.group(1)
    if not image_link.startswith("http://") and not image_link.startswith("https://"):
        uploaded_urls = upload_images(
            container,
            conn_str,
            image_folder,
            [image_link],
            overwrite=True,
        )
        image_link = uploaded_urls[0]
    return f'<img src="{image_link}" class="origin_image zh-lightbox-thumb lazy">\n'


def main():
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

    os.makedirs(output_folder, exist_ok=True)

    for file_path in files:
        output_file_path = os.path.join(output_folder, os.path.split(file_path)[1])
        with open(file_path, encoding="utf-8") as in_f, open(
            output_file_path, "w", encoding="utf-8"
        ) as out_f:
            content = in_f.read()
            new_content = OBSIDIAN_IMAGE_LINK_RE.sub(
                lambda m: process_image_link(
                    container, conn_str, image_link_root, m
                ),
                content,
            )
            new_content = convert_latex(new_content)
            out_f.write(new_content)


if __name__ == "__main__":
    main()
