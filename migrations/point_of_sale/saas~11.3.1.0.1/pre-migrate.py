# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(cr, *util.expand_braces("point_of_sale.access_{product,uom}_uom_manager"))
