import unittest

from htmlnode import *
from textnode import *


class TestHTMLNode(unittest.TestCase):
    def test_repr(self):
        node = HTMLNode("tag", "value", ["children"], {"test prop": "prop"})
        self.assertEqual(str(node), f"HTMLNode:\nTag: {"tag"}\nValue: {"value"}\nChildren: {["children"]}\nProperties: {dict({"test prop": "prop"})}")
    
    def test_none(self):
        node = HTMLNode()
        self.assertEqual(node.tag, None)
        self.assertEqual(node.value, None)
        self.assertEqual(node.children, None)
        self.assertEqual(node.props, None)
        self.assertEqual(node.props_to_html(), '')
    
    def test_props_to_html(self):
        node = HTMLNode(props={"test prop 1": 1, "test prop 2": "bababooey"})
        self.assertEqual(node.props_to_html(), f" test prop 1=\"{1}\" test prop 2=\"bababooey\"")
    
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a(self):
        node = LeafNode("a", "Hello, world!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), "<a href=\"https://www.google.com\">Hello, world!</a>")
    
    def test_leaf_to_html_div(self):
        node = LeafNode("div", "Hello, world!")
        self.assertEqual(node.to_html(), "<div>Hello, world!</div>")
    
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )
    
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = textnode_to_htmlnode(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
    
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )
    
    def test_markdown_to_blocks_newlines(self):
        md = """
This is **bolded** paragraph



This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )
    
    def test_blocks_to_blocktypes(self):
        blocks = [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ]
        self.assertEqual(
            list(map(block_to_blocktype, blocks)),
            [
                BlockTypes.PARA,
                BlockTypes.PARA,
                BlockTypes.U_LIST
            ]
        )
    
    def test_blocks_to_different_blocktypes(self):
        blocks = [
                "## Header 1",
                "###### Header 2",
                "```\nCOOOOOODE```",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
                "1. This\n2. is\n3. an\n4. ordered\n5. list",
                ">Make sure to test your shit - Sun Tzu"
            ]
        self.assertEqual(
            list(map(block_to_blocktype, blocks)),
            [
                BlockTypes.HEAD,
                BlockTypes.HEAD,
                BlockTypes.CODE,
                BlockTypes.PARA,
                BlockTypes.U_LIST,
                BlockTypes.O_LIST,
                BlockTypes.QUOTE
            ]
        )
    
    def test_blocks_to_invalid_blocktypes(self):
        blocks = [
                "## Header 1",
                "######Header 2",
                "```COOOOOODE```",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
                "1. This\n3. is\n3. an\n6. ordered\n7. list",
                "> Make sure to test your shit - Sun Tzu"
            ]
        self.assertEqual(
            list(map(block_to_blocktype, blocks)),
            [
                BlockTypes.HEAD,
                BlockTypes.PARA,
                BlockTypes.PARA,
                BlockTypes.PARA,
                BlockTypes.U_LIST,
                BlockTypes.PARA,
                BlockTypes.QUOTE
            ]
        )
    
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph text in a p tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = md_to_htmlnode(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = md_to_htmlnode(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )


if __name__ == "__main__":
    unittest.main()