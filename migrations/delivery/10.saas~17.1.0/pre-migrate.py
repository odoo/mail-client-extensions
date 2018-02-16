# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'delivery.carrier', 'free_if_more_than', 'free_over')
    util.remove_field(cr, 'delivery.carrier', 'price')
    util.remove_field(cr, 'delivery.carrier', 'available')
