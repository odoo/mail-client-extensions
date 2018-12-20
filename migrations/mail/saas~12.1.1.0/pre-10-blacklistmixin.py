# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "res_partner", "email_normalized", "varchar")
    cr.execute("""
        UPDATE res_partner
           SET email_normalized=lower(substring(email, '([^ ,;<@]+@[^> ,;]+)'))
         WHERE email IS NOT NULL
    """)
