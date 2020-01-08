# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""
        SELECT model, name
          FROM ir_model_fields
         WHERE state = 'manual'
           AND ttype = 'binary'
    """)
    for model, name in cr.fetchall():
        util.convert_binary_field_to_attachment(cr, model, name)
