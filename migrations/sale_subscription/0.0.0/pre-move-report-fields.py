from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("saas~16.3"):
        for field in ["is_abandoned_cart", "website_id"]:
            if util.ref(cr, "sale_subscription.field_sale_subscription_report__{}".format(field)):
                if util.module_installed(cr, "website_sale"):
                    util.move_field_to_module(
                        cr, "sale.subscription.report", field, "sale_subscription", "website_sale"
                    )
                else:
                    util.remove_field(cr, "sale.subscription.report", field)
