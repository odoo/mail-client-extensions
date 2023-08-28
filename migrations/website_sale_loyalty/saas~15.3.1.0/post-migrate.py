# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE loyalty_program loyalty
           SET website_id = coupon.website_id
          FROM coupon_program coupon
         WHERE coupon.id = loyalty._upg_coupon_program_id
           AND coupon.website_id IS NOT NULL
        """
    )
