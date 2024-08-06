from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "account_account_account_asset_rel", "account_account", "account_asset")
    query = """
            INSERT INTO account_account_account_asset_rel (account_account_id, account_asset_id)
            SELECT id, asset_model
              FROM account_account
             WHERE asset_model IS NOT NULL
        """
    cr.execute(query)
    util.remove_column(cr, "account_account", "asset_model")
    util.rename_field(cr, "account.account", "asset_model", "asset_model_ids")
