from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "sale_product_configurator", "sale")
    util.merge_module(cr, "pos_sale_product_configurator", "pos_sale")
    util.merge_module(cr, "website_sale_product_configurator", "website_sale")

    util.remove_module(cr, "documents_spreadsheet_account")
    util.remove_module(cr, "documents_spreadsheet_crm")

    if util.has_enterprise():
        util.merge_module(cr, "website_sale_renting_product_configurator", "website_sale_renting")
        util.new_module(cr, "accountant", deps={"account_accountant"})
        util.force_install_module(cr, "accountant", if_installed=["account_accountant"])
        util.force_upgrade_of_fresh_module(cr, "account_accountant")
        util.force_upgrade_of_fresh_module(cr, "account_online_synchronization")
        util.force_upgrade_of_fresh_module(cr, "l10n_co_dian")
        util.remove_module(cr, "stock_barcode_account_barcodelookup")
    util.force_upgrade_of_fresh_module(cr, "hr_homeworking_calendar")

    # Remove obsolete module 'l10n_dk_bookkeeping'.
    # This is due to a new displayed, computed and stored field 'invoice_currency_rate' on account.move.
    # To compute the new field (for upgrade) we need the column 'l10n_dk_currency_rate_at_transaction'.
    # It is later removed in the pre-* phase of module 'account'.
    util.remove_field(cr, "account.move", "l10n_dk_currency_rate_at_transaction", drop_column=False)
    util.remove_module(cr, "l10n_dk_bookkeeping")

    if util.module_installed(cr, "account_budget"):
        # purchase is a new dependency of account_budget
        util.create_column(cr, "res_partner", "purchase_warn", "varchar", default="no-message")

        if not util.module_installed(cr, "account_accountant"):
            # account_accountant is also a new mult-level dependency of account_budget. This triggers the auto-install
            # of account_reports, account_asset, and account_followup. In real world DBs we do not expect account_budget
            # being installed without account_accountant. Ignored columns below, in comments the script computing them.
            util.ENVIRON["CI_IGNORE_NO_ORM_TABLE_CHANGE"].update(
                {
                    ("account.move.line", "exclude_bank_lines"),  # account_reports/saas~17.5.1.0/pre-migrate.py
                    ("account.move", "asset_move_type"),  # account_asset/saas~17.4.1.0/pre-migrate.py
                    ("account.move", "depreciation_value"),  # account_asset/16.0.1.0/pre-migrate.py
                }
            )
            util.create_column(cr, "res_partner", "followup_reminder_type", "varchar", default="automatic")
