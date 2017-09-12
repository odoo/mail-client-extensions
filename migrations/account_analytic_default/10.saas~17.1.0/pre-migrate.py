# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'product.template', 'rules_count')
    util.remove_field(cr, 'product.product', 'rules_count')
