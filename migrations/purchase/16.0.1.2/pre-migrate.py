from odoo.addons.base.maintenance.migrations.util.accounting import upgrade_analytic_distribution
from odoo.upgrade import util

eb = util.expand_braces


def migrate(cr, version):
    util.rename_field(cr, "purchase.order", *eb("tax_totals{_json,}"))
    util.remove_view(cr, "purchase.product_template_form_view")
    util.remove_view(cr, "purchase.view_category_property_form")

    upgrade_analytic_distribution(
        cr,
        model="purchase.order.line",
        account_field="account_analytic_id",
    )
    util.remove_field(cr, "purchase.report", "account_analytic_id")
    if util.module_installed(cr, "purchase_stock"):
        util.move_field_to_module(
            cr,
            "product.category",
            "property_account_creditor_price_difference_categ",
            "purchase",
            "purchase_price_diff",
        )
        util.move_field_to_module(
            cr, "product.template", "property_account_creditor_price_difference", "purchase", "purchase_price_diff"
        )
    else:
        util.remove_field(cr, "product.category", "property_account_creditor_price_difference_categ")
        util.remove_field(cr, "product.template", "property_account_creditor_price_difference")
