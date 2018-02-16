# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'hr_applicant', 'delay_close', 'float8')
    cr.execute("""
        UPDATE hr_applicant
           SET delay_close = extract(epoch from (date_closed - date_open)) / 86400
    """)

    util.remove_model(cr, 'hr.recruitment.report')
