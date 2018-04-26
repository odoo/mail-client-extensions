# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("DROP TABLE rule_partner_rel")
    cr.execute("DROP TABLE rule_product_rel")
    util.remove_field(cr, 'sale.coupon.rule', 'rule_partner_ids')
    util.remove_field(cr, 'sale.coupon.rule', 'rule_product_ids')
