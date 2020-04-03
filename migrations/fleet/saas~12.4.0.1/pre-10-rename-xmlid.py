# -*- coding: utf-8 -*-
from odoo.upgrade import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'fleet.brand_land rover', 'fleet.brand_land_rover')
    util.rename_xmlid(cr, 'fleet.brand_tesla motors', 'fleet.brand_tesla_motors')
    util.rename_xmlid(cr, 'fleet.brand_corre la licorne', 'fleet.brand_corre_la_licorne')
