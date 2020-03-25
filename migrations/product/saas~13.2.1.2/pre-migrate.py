# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "product.price_list")  # no, there aren't any typo. `product.pricelist` is still there

    util.force_noupdate(cr, "product.report_pricelist", False)
