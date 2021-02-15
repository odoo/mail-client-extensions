# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, 'stock.picking', 'delivery_packaging_ids', 'delivery_package_type_ids')
