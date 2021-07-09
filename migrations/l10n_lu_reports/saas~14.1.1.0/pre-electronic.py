# -*- coding: utf-8 -*-

"""
This file was moved from l10n_lu_reports_electronic_xml_2_0/saas~14.1.1.0.
The reason for this is that the module is merged into l10n_lu_reports in saas~14.5,
and it avoids creating a symlink.
The script will be executed even if l10n_lu_reports_electronic_xml_2_0 is not installed,
which is not a problem since it is only removing things.
"""

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "l10n.lu.report.partner.vat.intra")

    module = "l10n_lu_reports" if util.version_gte("saas~14.5") else "l10n_lu_reports_electronic"
    util.remove_record(cr, f"{module}.action_account_report_partner_vat_intra")
    util.remove_record(cr, f"{module}.menu_action_account_report_partner_vat_intra")
    util.remove_view(cr, f"{module}.search_template")
    util.remove_view(cr, f"{module}.search_template_intrastat_code")
