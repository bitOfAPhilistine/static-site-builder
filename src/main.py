import os
import shutil

from textnode import *
from htmlnode import *


PUBLIC_DIR = "public"
STATIC_DIR = "static"

def copy_dir(src, dst):
    print(f"Scanning {src}...")
    contents = os.listdir(src)
    print(contents)
    for item in contents:
        item_path = f"{src}/{item}"
        if os.path.isfile(item_path):
            print(f"Copying {item}...")
            shutil.copy(item_path, item_path.replace(src, dst))
        else:
            os.mkdir(item_path.replace(src, dst))
            copy_dir(item_path, item_path.replace(src, dst))

def extract_title(md):
    for line in md.split('\n'):
        if line.startswith("# "):
            return line[2:].strip()
    raise Exception("md file lacks title")

def generate_page(src, dst, template_path="template.html"):
    print(f"Generating page at {dst} from {src} using {template_path}...")

    md = ''
    template = ''
    with open(src) as s:
        md = s.read()
    with open(template_path) as t:
        template = t.read()
    
    title = extract_title(md)
    content = md_to_htmlnode(md).to_html()
    html = template.replace("{{ Title }}", title).replace("{{ Content }}", content)

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    print(f"Generating html file: {dst}...")
    with open(dst, mode='x') as out:
        out.write(html)

def generate_pages_recursive(src, dst, template_path="template.html"):
    contents = os.listdir(src)
    print(contents)
    for item in contents:
        item_path = f"{src}/{item}"
        if os.path.isfile(item_path):
            generate_page(item_path, item_path.replace(src, dst).replace(".md", ".html"))
        else:
            generate_pages_recursive(item_path, item_path.replace(src, dst).replace(".md", ".html"))

def main():
    if os.path.exists(PUBLIC_DIR):
        shutil.rmtree(PUBLIC_DIR)
        print("Cleared generated folder")
    
    if not os.path.exists(STATIC_DIR):
        raise FileNotFoundError("static dir not found!")

    os.mkdir(PUBLIC_DIR)
    print("Made new generated folder")

    print("Copying static folder to public...")
    copy_dir(STATIC_DIR, PUBLIC_DIR)
    print("Static folder copied to public!")

    generate_pages_recursive("content", f"{PUBLIC_DIR}")


main()