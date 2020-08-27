# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_de_reports.action_account_report_de_partner_vat_intra")
    util.remove_record(cr, "l10n_de_reports.menu_action_account_report_de_partner_vat_intra")
    util.remove_model(cr, "l10n.de.report.partner.vat.intra")
