# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    imp = util.import_script("delivery/10.saas~18.1.0/pre-rename.py")
    imp.extract_product(cr, "delivery_ups", "ups_us", "ups_us")
    imp.extract_product(cr, "delivery_ups", "ups_be", "ups_be")
