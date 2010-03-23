#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.parser.util   import (
    extract_tag_name,
    ParagraphNode, TextNode, SelfClosingTagNode
)

# ----------------------------------------------------------------------------

def empty_text(text):
    return text.isspace()

def empty_pred(node):
    if isinstance(node, TextNode):
        return empty_text(node.value)
    elif isinstance(node, SelfClosingTagNode):
        return extract_tag_name(node.value) == 'br'
    return False

def empty_paragraph(p):
    """ A paragraph is empty if it contains only empty text nodes and <br>s """
    return all(empty_pred(pnode) for pnode in p)

def empty_node(node):
    if isinstance(node, ParagraphNode):
        return empty_paragraph(node)
    return False

def filter_tree(tree):
    tree.children = [filter_tree(child_node) for child_node in \
            tree.children if not empty_node(child_node)]
    return tree

