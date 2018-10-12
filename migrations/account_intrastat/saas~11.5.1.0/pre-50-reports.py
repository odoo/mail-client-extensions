# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_model(cr, "report.intrastat")
    util.remove_view(cr, "account_intrastat.report_intrastatinvoice_document")
    util.remove_view(cr, "account_intrastat.report_intrastatinvoice")
