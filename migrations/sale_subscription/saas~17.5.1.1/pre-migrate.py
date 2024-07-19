from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "project_sale_subscription"):
        util.move_field_to_module(
            cr, "account.analytic.account", "subscription_count", "sale_subscription", "project_sale_subscription"
        )
        util.move_field_to_module(
            cr, "account.analytic.account", "subscription_ids", "sale_subscription", "project_sale_subscription"
        )
        util.rename_xmlid(
            cr,
            "sale_subscription.account_analytic_account_view_inherit_sale_subscription",
            "project_sale_subscription.account_analytic_account_view_inherit_project_sale_subscription",
        )
    else:
        util.remove_field(cr, "account.analytic.account", "subscription_count")
        util.remove_field(cr, "account.analytic.account", "subscription_ids")
        util.remove_view(cr, "sale_subscription.account_analytic_account_view_inherit_sale_subscription")
