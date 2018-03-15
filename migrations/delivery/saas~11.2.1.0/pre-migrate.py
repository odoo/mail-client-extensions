# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'delivery.mail_template_data_delivery_notification')

    util.remove_field(cr, 'stock.move', 'weight_uom_id')
    util.remove_column(cr, 'stock.picking', 'weight_uom_id')    # column still exists (non stored)
    util.remove_field(cr, 'stock.picking', 'number_of_packages')
