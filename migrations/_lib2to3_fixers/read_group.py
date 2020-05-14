"""
Fixer for read_group().

This converts `.read_group(domain, 'f', 'f')` into `.read_group(domain, ['f'], 'f')`.
See unit test `test_read_group_refactor.py` for examples.
"""

from lib2to3.fixer_base import BaseFix
from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols as syms
from lib2to3.pytree import Leaf, Node


class FixReadGroup(BaseFix):

    PATTERN = """
        power< any*
            trailer<
                '.' 'read_group'
            > trailer<
                '('
                arglist<any ',' fields=STRING any*>
                ')'
            >
        >
    """

    def transform(self, node, results):
        leaf = results.get("fields")
        leaf_clone = leaf.clone()
        leaf_clone.prefix = ""
        leaf.replace(Node(syms.atom, [Leaf(token.LSQB, "[", prefix=leaf.prefix), leaf_clone, Leaf(token.RSQB, "]")]))
