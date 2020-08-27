# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "l10n_lu_reports_electronic.SCodeNode", "l10n_lu_reports.SCodeNode")
    util.rename_xmlid(cr, "l10n_lu_reports_electronic.LTCodeNode", "l10n_lu_reports.LTCodeNode")
    util.rename_xmlid(cr, "l10n_lu_reports_electronic.IntrastatLuXMLReport", "l10n_lu_reports.EcSalesLuXMLReport")
