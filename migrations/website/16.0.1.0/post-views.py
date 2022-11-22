# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Remove website.assets_editor bundle from COWed layouts
    cr.execute(
        r"""
        SELECT v.id
          FROM ir_ui_view v
     LEFT JOIN ir_model_data d
            ON d.model = 'ir.ui.view'
           AND d.res_id = v.id
         WHERE d.id IS NULL
           AND v.key = 'website.layout'
           AND v.arch_db::text LIKE '%website.assets\_editor%'
    """
    )
    view_ids = cr.fetchall()
    for view in view_ids:
        with util.edit_view(cr, view_id=view) as arch:
            for tcall in arch.xpath('//t[@t-call-assets="website.assets_editor"]'):
                parent = tcall.getparent()
                if len(parent.getchildren()) == 1:
                    parent.getparent().remove(parent)
                else:
                    parent.remove(tcall)
