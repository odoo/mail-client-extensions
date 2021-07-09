# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_partner", "l10n_lu_agent_matr_number", "varchar")
    util.create_column(cr, "res_partner", "l10n_lu_agent_ecdf_prefix", "varchar")
    util.create_column(cr, "res_partner", "l10n_lu_agent_rcs_number", "varchar")

    util.remove_view(cr, "l10n_lu_reports.SourceDocumentsTemplate")
    util.remove_view(cr, "l10n_lu_reports.IntrastatLuXMLReport")
    util.remove_view(cr, "l10n_lu_reports.l10n_lu_electronic_report_template")
    util.remove_view(cr, "l10n_lu_reports.view_l10n_lu_generate_xml")
