# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # create column in db for new fields in purchase_order table
    util.create_column(cr, "purchase_order", "l10n_in_gst_treatment", "varchar")
