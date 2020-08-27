# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_lu_reports_electronic.action_account_report_partner_vat_intra")
    util.remove_record(cr, "l10n_lu_reports_electronic.menu_action_account_report_partner_vat_intra")
    util.remove_model(cr, "l10n.lu.report.partner.vat.intra")
    util.remove_view(cr, "l10n_lu_reports_electronic.search_template")
    util.remove_view(cr, "l10n_lu_reports_electronic.search_template_intrastat_code")
