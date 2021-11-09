# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(
        cr,
        "hr_payroll.mail_template_new_payslip",
        util.update_record_from_xml,
        reset_translations={"subject", "body_html"},
    )
