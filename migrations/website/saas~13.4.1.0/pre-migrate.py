# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_attachment
           SET url = '/'||url
         WHERE type='url'
           AND url ilike 'theme_%'
           AND res_model = 'ir.module.module'
    """
    )

    cr.execute(
        """
        INSERT INTO ir_ui_view_group_rel
             SELECT id, visibility_group
               FROM ir_ui_view
              WHERE visibility_group is not null
        ON CONFLICT DO NOTHING
        """
    )
    util.remove_field(cr, "ir.ui.view", "visibility_group")
