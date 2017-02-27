# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'mail_followers', 'res_model_id', 'int4')
    cr.execute("""
        UPDATE mail_followers f
           SET res_model_id = m.id
          FROM ir_model m
         WHERE m.model = f.res_model
    """)
    cr.execute("DELETE FROM mail_followers WHERE res_model_id IS NULL")
