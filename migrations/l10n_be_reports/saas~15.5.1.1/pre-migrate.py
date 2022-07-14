# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_model(cr, "l10n.be.report.partner.vat.listing")
    util.remove_view(cr, "l10n_be_reports.line_caret_options")
