# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "l10n_sa_invoice", "l10n_sa")
    util.modules_auto_discovery(cr)

    if util.has_enterprise():
        util.remove_module(cr, "delivery_barcode")
