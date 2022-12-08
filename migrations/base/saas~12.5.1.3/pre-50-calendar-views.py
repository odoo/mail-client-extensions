# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT id
          FROM ir_ui_view
         WHERE type='calendar'
           AND arch_db ilike '%readonly_form_view_id%'
        """
    )
    for (view_id,) in cr.fetchall():
        with util.edit_view(cr, view_id=view_id, active=None) as view:
            for node in view.xpath("//calendar[@readonly_form_view_id]"):
                del node.attrib["readonly_form_view_id"]
