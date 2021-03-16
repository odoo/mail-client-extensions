# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    if util.has_enterprise():
        util.merge_module(cr, "l10n_be_hr_payroll_eco_vouchers", "l10n_be_hr_payroll")

        util.new_module(
            cr, "mass_mailing_sale_subscription", deps={"mass_mailing", "sale_subscription"}, auto_install=True
        )
        util.remove_module(cr, "l10n_be_sale_intrastat")
        util.new_module(cr, "data_merge_project", deps={"data_merge", "project"}, auto_install=True)
        util.new_module(cr, "data_merge_helpdesk", deps={"data_merge", "helpdesk"}, auto_install=True)
