# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.move_field_to_module(cr, "account.move", "partner_shipping_id", "sale", "account")
    util.move_field_to_module(cr, "res.config.settings", "group_delivery_invoice_address", "sale", "account")
    util.create_column(cr, "account_move", "is_storno", "bool", default=False)
    util.create_column(cr, "account_chart_template", "use_storno_accounting", "bool", default=False)
    util.create_column(cr, "res_company", "account_storno", "bool", default=False)
    util.rename_xmlid(cr, *eb("{sale,account}.group_delivery_invoice_address"))
