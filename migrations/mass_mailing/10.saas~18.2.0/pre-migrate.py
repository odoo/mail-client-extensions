# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'mail_mass_mailing', 'mailing_model_id', 'int4')
    cr.execute("""
        UPDATE mail_mass_mailing m
           SET mailing_model_id = i.id
          FROM ir_model i
         WHERE i.model = m.mailing_model
    """)
    util.remove_field(cr, 'mail.mass_mailing', 'mailing_model')
