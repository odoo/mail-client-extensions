# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # remove view loading deprecated files
    util.remove_record(cr, "theme_loftspace_sale.assets_frontend")
