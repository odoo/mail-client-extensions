# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "mail_mass_mailing_contact", "email_normalized", "varchar")
    cr.execute("""
        UPDATE mail_mass_mailing_contact
           SET email_normalized=lower(substring(email, '([^ ,;<@]+@[^> ,;]+)'))
         WHERE email IS NOT NULL
    """)
