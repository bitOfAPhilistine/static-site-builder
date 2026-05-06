import re

from enum import Enum


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class TextNode():
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url
    
    def __eq__(self, other):
        return self.text == other.text and self.text_type == other.text_type and self.url == other.url

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type}, {self.url})"

def split_nodes_delimiter(old_nodes: list, delimiter: str, text_type: TextType):
    if len(delimiter) == 0:
        raise ValueError("delimiter must be at least 1 character long")
        
    nodes = []
    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            text = node.text
            dl_length = len(delimiter)
            block_open = False
            has_been_split = False
            current_block_start = 0
            current_block_end = 0
            
            for i in range(len(text) - dl_length + 1):
                if text[i:].startswith(delimiter):
                    block_open = not block_open
                    if block_open:
                        current_block_start = i + dl_length
                        if i > 0:
                            if not has_been_split:
                                nodes.append(TextNode(text[:i], TextType.TEXT))
                            else:
                                nodes.append(TextNode(text[current_block_end + dl_length:i], TextType.TEXT))
                            has_been_split = True
                    else:
                        current_block_end = i
                        nodes.append(TextNode(text[current_block_start:current_block_end], text_type))
                        has_been_split = True

            if block_open:
                raise Exception("invalid markdown formatting")

            if not has_been_split:
                nodes.append(node)
            elif current_block_end != len(text) - dl_length:
                nodes.append(TextNode(text[current_block_end + dl_length:], TextType.TEXT))
        else:
            nodes.append(node)
    
    return nodes

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def split_nodes_images(old_nodes: list):
    nodes = []
    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            text = node.text
            images = extract_markdown_images(text)
            
            for image in images:
                split_text = text.split(f"![{image[0]}]({image[1]})", 1)
                if len(split_text[0]) > 0:
                    nodes.append(TextNode(split_text[0], TextType.TEXT))
                nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))
                text = split_text[1]
            
            if len(text) > 0:
                nodes.append(TextNode(text, TextType.TEXT))
        else:
            nodes.append(node)
    
    return nodes

def split_nodes_links(old_nodes: list):
    nodes = []
    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            text = node.text
            links = extract_markdown_links(text)
            
            for link in links:
                split_text = text.split(f"[{link[0]}]({link[1]})", 1)
                nodes.append(TextNode(split_text[0], TextType.TEXT))
                nodes.append(TextNode(link[0], TextType.LINK, link[1]))
                text = split_text[1]
            
            if len(text) > 0:
                nodes.append(TextNode(text, TextType.TEXT))
        else:
            nodes.append(node)
    
    return nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    has_bold = "**" in text
    has_italic = "_" in text
    has_code = "`" in text
    has_images = len(extract_markdown_images(text)) > 0
    has_links = len(extract_markdown_links(text)) > 0

    if has_bold:
        nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    if has_italic:
        nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    if has_code:
        nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    if has_images:
        nodes = split_nodes_images(nodes)
    if has_links:
        nodes = split_nodes_links(nodes)
    
    return nodes
    