# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # create column in db for new fields in sale_order table
    util.create_column(cr, "sale_order", "l10n_in_gst_treatment", "varchar")

    # create column in db for new fields in res_partner table
    util.create_column(cr, "res_partner", "l10n_in_shipping_gstin", "varchar")
