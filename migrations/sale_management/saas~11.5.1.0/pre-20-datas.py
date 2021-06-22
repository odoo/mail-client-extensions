# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    renames = util.splitlines(
        """
        report_saleorder_{validity_date,document_inherit_sale_management}

        access_sale_{quote,order}_template
        access_sale_{quote,order}_template_manager
        access_sale_{quote,order_template}_line
        access_sale_{quote,order_template}_line_manager
        access_sale_{quote,order_template}_option
        access_sale_order_option
        access_sale_order_option_all
    """
    )
    for rename in renames:
        if "{" in rename:
            f, t = eb(rename)
        else:
            f = t = rename
        util.rename_xmlid(cr, "sale_quotation_builder." + f, "sale_management." + t)

    util.rename_xmlid(
        cr, "sale_quotation_builder.view_sale_quote_template_form", "sale_management.sale_order_template_view_form"
    )
    util.rename_xmlid(
        cr, "sale_quotation_builder.view_sale_quote_template_tree", "sale_management.sale_order_template_view_tree"
    )
    util.rename_xmlid(
        cr,
        "sale_quotation_builder.optional_products",
        "sale_management.sale_order_portal_content_inherit_sale_management",
    )
