# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        SELECT id
          FROM ir_model_fields
         WHERE state='manual'
           AND related IS NOT NULL
           AND related_field_id IS NULL
    """)
    fields = util.env(cr)['ir.model.fields'].browse([x[0] for x in cr.fetchall()])
    fields._compute_related_field_id()
