# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("ALTER TABLE helpdesk_ticket_sale_coupon_rel RENAME TO coupon_coupon_helpdesk_ticket_rel")
    cr.execute("ALTER TABLE coupon_coupon_helpdesk_ticket_rel RENAME COLUMN sale_coupon_id TO coupon_coupon_id")
