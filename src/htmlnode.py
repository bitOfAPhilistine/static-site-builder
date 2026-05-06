import functools

from enum import Enum
from textnode import *


class BlockTypes(Enum):
    PARA = "paragraph"
    HEAD = "heading"
    CODE = "code"
    QUOTE = "quote"
    U_LIST = "unordered list"
    O_LIST = "ordered list"

class HTMLNode():
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props
    
    def __repr__(self):
        return f"HTMLNode:\nTag: {self.tag}\nValue: {self.value}\nChildren: {self.children}\nProperties: {self.props}"

    def to_html(self):
        raise NotImplementedError()

    def props_to_html(self):
        if self.props == None or len(self.props) == 0:
            return ''

        output = ""
        for prop in self.props:
            output += f" {prop}=\"{self.props[prop]}\""
        return output

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, props=props)
    
    def __repr__(self):
        return f"HTMLNode:\nTag: {self.tag}\nValue: {self.value}\nProperties: {self.props}"
    
    def to_html(self):
        if self.value == None:
            raise ValueError("leaf node lacks value")
        
        if self.tag == None:
            return self.value

        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, children=children, props=props)
    
    def __repr__(self):
        return f"HTMLNode:\nTag: {self.tag}\nValue: {self.value}\nProperties: {self.props}"
    
    def to_html(self):
        if self.tag == None:
            raise ValueError("parent node lacks tag")
        if self.children == None or len(self.children) == 0:
            raise ValueError("parent node lacks children")

        output = f"<{self.tag}{self.props_to_html()}>"
        for child in self.children:
            output += child.to_html()
        output += f"</{self.tag}>"
        return output


def textnode_to_htmlnode(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode('b', text_node.text)
        case TextType.ITALIC:
            return LeafNode('i', text_node.text)
        case TextType.CODE:
            return LeafNode('code', text_node.text)
        case TextType.LINK:
            return LeafNode('a', text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode('img', '', {"src": text_node.url, "alt": text_node.text})
        case _:
            raise Exception("invalid TextType")

def markdown_to_blocks(md: str):
    return list(filter(lambda block: len(block) > 0, list(map(lambda block: block.strip(), md.split("\n\n")))))

def block_to_blocktype(block: str):
    if block.startswith("# ") or block.startswith("## ") or block.startswith("### ") or block.startswith("#### ") or block.startswith("##### ") or block.startswith("###### "):
        return BlockTypes.HEAD
    
    if block.startswith("```\n") and block.endswith("```"):
        return BlockTypes.CODE
    
    if block.startswith(">"):
        return BlockTypes.QUOTE
    
    if block.startswith("- "):
        lines = block.split("\n")
        confirmed = True
        for line in lines:
            if not line.startswith("- "):
                confirmed = False
        if confirmed:
            return BlockTypes.U_LIST
    
    if block.startswith("1. "):
        lines = block.split("\n")
        confirmed = True
        current_number = 1
        for line in lines:
            if line.startswith(f"{current_number}. "):
                current_number += 1
            else:
                confirmed = False
        if confirmed:
            return BlockTypes.O_LIST
    
    return BlockTypes.PARA

def block_to_htmlnodes(block):
    return list(map(textnode_to_htmlnode, text_to_textnodes(block)))

def md_to_htmlnode(md):
    blocks = markdown_to_blocks(md)
    nodes = []

    for block in blocks:
        type = block_to_blocktype(block)

        match type:
            case BlockTypes.PARA:
                nodes.append(ParentNode('p', block_to_htmlnodes(block)))
            case BlockTypes.HEAD:
                hashtag_count = 0
                for c in block:
                    if c == '#':
                        hashtag_count += 1
                    else:
                        break
                nodes.append(ParentNode(f'h{hashtag_count}', block_to_htmlnodes(block[1 + hashtag_count:])))
            case BlockTypes.CODE:
                nodes.append(ParentNode('pre', [textnode_to_htmlnode(TextNode(block.lstrip("`\n").rstrip("`"), TextType.CODE))]))
            case BlockTypes.QUOTE:
                if block.startswith("> "):
                    nodes.append(ParentNode('blockquote', block_to_htmlnodes(block[2:])))
                else:
                    nodes.append(ParentNode('blockquote', block_to_htmlnodes(block[1:])))
            case BlockTypes.U_LIST:
                lines = list(map(lambda entry: entry.strip(), block.split('\n-')))
                children = [ParentNode('li', block_to_htmlnodes(lines[0][2:]))]
                for line in lines[1:]:
                    children.append(ParentNode('li', block_to_htmlnodes(line)))
                nodes.append(ParentNode('ul', children))
            case BlockTypes.O_LIST:
                lines = block.split('\n')
                children = []
                for line in lines:
                    children.append(ParentNode('li', block_to_htmlnodes(line.strip(" 1234567890."))))
                nodes.append(ParentNode('ol', children))
            case _:
                raise ValueError("invalid blocktype")
    
    return ParentNode("div", nodes)