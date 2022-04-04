# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Migrate `coupon_ids` m2m `coupon.coupon` -> `loyalty.card`
    util.create_m2m(cr, "helpdesk_ticket_loyalty_card_rel", "helpdesk_ticket", "loyalty_card")
    cr.execute(
        """
        INSERT INTO helpdesk_ticket_loyalty_card_rel (
            helpdesk_ticket_id, loyalty_card_id
        )
        SELECT rel.helpdesk_ticket_id, c.id
          FROM coupon_coupon_helpdesk_ticket_rel rel
          JOIN loyalty_card c
            ON c._upg_coupon_coupon_id = rel.coupon_coupon_id
        """
    )
    cr.execute("DROP TABLE coupon_coupon_helpdesk_ticket_rel")

    util.rename_xmlid(
        cr,
        "helpdesk_sale_loyalty.access_helpdesk_sale_coupon_generate_helpdesk",
        "helpdesk_sale_loyalty.access_helpdesk_sale_coupon_generate",
    )

    util.remove_model(cr, "helpdesk.sale.coupon")
