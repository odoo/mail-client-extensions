# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_model(cr, "l10n_in.account.invoice.report")
    util.remove_model(cr, "l10n_in.payment.report")
    util.remove_model(cr, "l10n_in.advances.payment.report")
    util.remove_model(cr, "l10n_in.advances.payment.adjustment.report")
    util.remove_model(cr, "l10n_in.exempted.report")
    util.remove_model(cr, "l10n_in.product.hsn.report")
