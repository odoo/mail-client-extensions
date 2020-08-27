# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "l10n.be.report.partner.vat.intra")
    util.remove_record(cr, "l10n_be_reports.action_account_report_partner_vat_intra")
    util.remove_record(cr, "l10n_be_reports.menu_action_account_report_partner_vat_intra")
