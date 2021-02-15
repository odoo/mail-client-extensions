# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, 'delivery.carrier', 'fedex_default_packaging_id', 'fedex_default_package_type_id')
