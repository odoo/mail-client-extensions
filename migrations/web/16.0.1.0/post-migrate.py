# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        r"""
        SELECT id
          FROM ir_ui_view
         WHERE key = 'web.frontend_layout'
           AND arch_db->>'en_US' LIKE '%web.debug\_icon%'
        """
    )
    for view_id in cr.fetchall():
        with util.edit_view(cr, view_id=view_id) as arch:
            for node in arch.xpath('//t[@t-call="web.debug_icon"]'):
                node.getparent().remove(node)
