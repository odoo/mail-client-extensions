# -*- coding: utf-8 -*-

from odoo.upgrade import util


def _openerp(cr, version):
    cr.execute(
        """
        DELETE FROM ir_model_data
              WHERE module = 'account_taxcloud'
                AND name = 'account_fiscal_position_taxcloud_us'
    """
    )

    util.uninstall_module(cr, "website_sale_taxcloud_delivery")
    util.uninstall_module(cr, "website_sale_account_taxcloud")
    util.uninstall_module(cr, "sale_subscription_taxcloud")
    util.uninstall_module(cr, "sale_account_taxcloud")
    util.uninstall_module(cr, "account_taxcloud")


def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {"8851207e-1ff9-11e0-a147-001cc0f2115e": _openerp})
    util.merge_module(cr, "l10n_sa_invoice", "l10n_sa")
    util.merge_module(cr, "sale_project_account", "sale_project")
    util.merge_module(cr, "account_sale_timesheet", "sale_project")

    # Coupon migration
    util.rename_module(cr, "coupon", "loyalty")
    util.merge_module(cr, "gift_card", "loyalty")
    util.force_upgrade_of_fresh_module(cr, "loyalty")

    util.rename_module(cr, "sale_coupon", "sale_loyalty")
    util.merge_module(cr, "sale_gift_card", "sale_loyalty")
    # This is required in case only sale_gift_card was installed.
    util.force_upgrade_of_fresh_module(cr, "sale_loyalty")

    util.rename_module(cr, "sale_coupon_delivery", "sale_loyalty_delivery")
    util.rename_module(cr, "sale_coupon_taxcloud", "sale_loyalty_taxcloud")
    util.rename_module(cr, "sale_coupon_taxcloud_delivery", "sale_loyalty_taxcloud_delivery")

    util.rename_module(cr, "website_sale_coupon", "website_sale_loyalty")
    util.merge_module(cr, "website_sale_gift_card", "website_sale_loyalty")
    # Same as sale_loyalty.
    util.force_upgrade_of_fresh_module(cr, "website_sale_loyalty")

    util.rename_module(cr, "website_sale_coupon_delivery", "website_sale_loyalty_delivery")
    util.merge_module(cr, "website_sale_delivery_giftcard", "website_sale_loyalty_delivery")
    if util.has_enterprise():
        util.rename_module(cr, "helpdesk_sale_coupon", "helpdesk_sale_loyalty")

    if util.has_enterprise():
        util.merge_module(cr, "pos_coupon", "pos_loyalty")
    else:
        util.rename_module(cr, "pos_coupon", "pos_loyalty")

    util.merge_module(cr, "pos_gift_card", "pos_loyalty")

    # Same as sale_loyalty.
    util.force_upgrade_of_fresh_module(cr, "pos_loyalty")

    # Required due to a precompute on products.
    util.force_upgrade_of_fresh_module(cr, "loyalty_delivery")

    if util.has_enterprise():
        util.remove_module(cr, "delivery_barcode")
        util.remove_module(cr, "sale_subscription_timesheet")
        util.force_upgrade_of_fresh_module(cr, "sale_temporal")
