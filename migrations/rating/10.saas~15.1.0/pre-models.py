# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'rating_rating', 'res_model_id', 'int4')
    cr.execute("""
        UPDATE rating_rating r
           SET res_model_id = m.id
          FROM ir_model m
         WHERE m.model = r.res_model
    """)
    cr.execute("DELETE FROM rating_rating WHERE res_model_id IS NULL")
