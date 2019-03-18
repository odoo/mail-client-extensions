# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    cr.execute("""
        SELECT model, array_agg(id)
          FROM ir_model_fields
         WHERE state = 'manual'
           AND related IS NOT NULL
           AND related_field_id IS NULL
      GROUP BY model
    """)
    for model, ids in cr.fetchall():
        if model in env:
            env["ir.model.fields"].browse(ids)._compute_related_field_id()
        else:
            # TODO handle manually unknow models
            pass
