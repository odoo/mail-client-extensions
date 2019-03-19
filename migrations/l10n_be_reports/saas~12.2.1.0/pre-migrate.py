# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_model(cr, "account.financial.html.report.export", "l10n_be_reports.periodic.vat.xml.export")
