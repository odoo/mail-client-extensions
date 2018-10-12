# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "product.template", "quote_description", "quotation_only_description")
    util.remove_field(cr, "sale.order", "quote_viewed")
    util.remove_field(cr, "sale.order.line", "option_line_id")
    util.remove_field(cr, "res.config.settings", "default_template_id")

    util.remove_view(cr, "sale_quotation_builder.sale_order_form_quote")
    util.remove_view(cr, "sale_quotation_builder.res_config_settings_view_form")
