# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("ALTER TABLE sale_coupon_program_sale_order_rel RENAME TO coupon_program_sale_order_rel")
    cr.execute("ALTER TABLE coupon_program_sale_order_rel RENAME COLUMN sale_coupon_program_id TO coupon_program_id")
