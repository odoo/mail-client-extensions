# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    field_names = """
        accounting_remuneration
        ip
        ip_deduction
        rep_fees
        car_priv
        car_atn
        mobile_atn
        internet_atn
        laptop_atn
        onss_employer
        onss_ffe""".split()

    for field_name in field_names:
        util.remove_field(cr, "hr.payroll.report", f"l10n_be_{field_name}")
