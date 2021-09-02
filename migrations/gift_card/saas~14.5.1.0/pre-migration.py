# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "gift.card", "buy_line_id", "gift_card", "sale_gift_card")
    util.move_field_to_module(cr, "sale.order.line", "gift_card_id", "gift_card", "sale_gift_card")
    util.move_field_to_module(cr, "gift.card", "redeem_line_ids", "gift_card", "sale_gift_card")
    util.move_field_to_module(cr, "sale.order", "gift_card_count", "gift_card", "sale_gift_card")
    util.move_field_to_module(cr, "sale.order.line", "generated_gift_card_ids", "gift_card", "sale_gift_card")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{,sale_}gift_card.gift_card_sale_order_action"))
    util.rename_xmlid(cr, *eb("{,sale_}gift_card.sale_order_view_extend_gift_card_form"))
    util.rename_xmlid(cr, *eb("{,sale_}gift_card.used_gift_card"))
    util.rename_xmlid(cr, *eb("{,sale_}gift_card.sale_order_portal_content_inherit"))
    util.rename_xmlid(cr, *eb("{,sale_}gift_card.sale_purchased_gift_card"))
    util.rename_xmlid(cr, *eb("{,sale_}gift_card.mail_template_gift_card"))
    util.rename_xmlid(cr, *eb("{,sale_}gift_card.access_gift_card_sales"))
    util.rename_xmlid(cr, *eb("{,sale_}gift_card.access_gift_card_manager"))

    util.parallel_execute(cr, util.explode_query_range(cr, """
        UPDATE product_template
           SET detailed_type = 'gift'
         WHERE is_gift_card = TRUE
    """, table="product_template"))
    util.remove_field(cr, 'product.template', 'is_gift_card')
