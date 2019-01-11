# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    cr.execute("""
        UPDATE ir_config_parameter
           SET key='sale.automatic_invoice'
         WHERE key='website_sale.automatic_invoice'
    """)

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("sale.transaction_form_inherit_sale{_payment,}"))
    util.rename_xmlid(cr, *eb("sale.action_quotations{,_with_onboarding}"))
    util.remove_record(cr, "sale.action_product_sale_list")

    util.remove_view(cr, "sale.report_invoice_layouted")
    util.remove_record(cr, "sale.group_sale_layout")

    util.remove_view(cr, "sale.invoice_form_inherit_sale")
    util.remove_view(cr, "sale.view_order_form_inherit_sale_stock_inherit_sale_order_dates")
    util.remove_view(cr, "sale.view_order_tree_date")
    util.remove_view(cr, "sale.view_quotation_tree_date")

    util.remove_view(cr, "sale.assets_backend")
    util.remove_view(cr, "sale.assets_frontend")

    util.remove_view(cr, "sale.portal_order_page")
    util.remove_view(cr, "sale.portal_order_error")
    util.remove_view(cr, "sale.portal_order_success")

    util.remove_record(cr, "sale.report_all_channels_sales")
    util.remove_record(cr, "sale.menu_attribute_action")
    util.remove_record(cr, "sale.menu_variants_action")
    util.remove_record(cr, "sale.menu_product_category_config_sale")

    util.if_unchanged(cr, "sale.email_template_edi_sale", util.update_record_from_xml)

    subtype_id = util.ref(cr, "sale.mt_order_confirmed")
    cr.execute("""
        UPDATE sale_order
        SET confirmation_date=c.thedate
        FROM (select res_id, min(create_date) as thedate
             from mail_message
             where subtype_id=%s and model='sale.order'
             and res_id in (select id from sale_order where confirmation_date IS NULL and state='sale')
             group by res_id) as c
        WHERE c.res_id=sale_order.id
    """, (subtype_id, ))
