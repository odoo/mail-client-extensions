# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, 'delivery.carrier', 'dhl_default_packaging_id', 'dhl_default_package_type_id')
