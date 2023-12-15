from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "sale_product_configurator", "sale")
    util.merge_module(cr, "pos_sale_product_configurator", "pos_sale")
    util.merge_module(cr, "website_sale_product_configurator", "website_sale")

    if util.has_enterprise():
        util.merge_module(cr, "website_sale_renting_product_configurator", "website_sale_renting")
    util.force_upgrade_of_fresh_module(cr, "hr_homeworking_calendar")

    # Remove obsolete module 'l10n_dk_bookkeeping'.
    # This is due to a new displayed, computed and stored field 'invoice_currency_rate' on account.move.
    # To compute the new field (for upgrade) we need the column 'l10n_dk_currency_rate_at_transaction'.
    # It is later removed in the pre-* phase of module 'account'.
    util.remove_field(cr, "account.move", "l10n_dk_currency_rate_at_transaction", drop_column=False)
    util.remove_module(cr, "l10n_dk_bookkeeping")
