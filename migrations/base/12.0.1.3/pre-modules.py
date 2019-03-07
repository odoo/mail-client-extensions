# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "l10n_it_edi", deps={"l10n_it"})  # see odoo/odoo#30845
    if util.has_enterprise():
        util.new_module(cr, "l10n_uk_reports_hmrc", deps={"l10n_uk_reports"}, auto_install=True)
