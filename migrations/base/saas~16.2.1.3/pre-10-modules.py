# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_module(cr, "website_payment_paypal")
    util.merge_module(cr, "l10n_generic_coa", "account")
    util.merge_module(cr, "l10n_multilang", "account")
    util.merge_module(cr, "l10n_in_tcs_tds", "l10n_in")

    if util.has_enterprise():
        util.remove_module(cr, "l10n_generic_auto_transfer_demo")
        util.remove_module(cr, "event_barcode_mobile")
        util.remove_module(cr, "hr_attendance_mobile")
        util.remove_module(cr, "barcodes_mobile")
        util.remove_module(cr, "project_timesheet_synchro")
    util.merge_module(cr, "purchase_price_diff", "purchase_stock")

    force_installs = set()
    if util.modules_installed(cr, "l10n_be_hr_payroll"):
        force_installs |= {"l10n_be_hr_payroll_sd_worx"}

    util.modules_auto_discovery(cr, force_installs=force_installs)
