# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, 'delivery.carrier', 'ups_default_packaging_id', 'ups_default_package_type_id')
