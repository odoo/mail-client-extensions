# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    imp = util.import_script("delivery/10.saas~18.1.0/pre-rename.py")
    imp.extract_product(cr, "delivery_dhl", "dhl_dom", "dhl_usa")
    imp.extract_product(cr, "delivery_dhl", "dhl_intl", "dhl_intl")
