# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    if util.column_exists(cr, "coupon_program", "website_id"):
        cr.execute(
            """
            UPDATE loyalty_program loyalty
               SET website_id = coupon.website_id
              FROM coupon_program coupon
             WHERE coupon.id = loyalty._upg_coupon_program_id
               AND coupon.website_id IS NOT NULL
            """
        )
