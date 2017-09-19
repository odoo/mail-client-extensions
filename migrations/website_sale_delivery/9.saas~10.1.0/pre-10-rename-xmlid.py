# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'website_sale_delivery.view_delivery_carrier_form',
                      'website_sale_delivery.view_delivery_carrier_form_website_delivery')
