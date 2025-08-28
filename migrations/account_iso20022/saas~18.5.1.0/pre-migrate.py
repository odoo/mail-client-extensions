from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "account_online_payment"):
        util.move_field_to_module(cr, "account.payment", "end_to_end_id", "account_online_payment", "account_iso2022")
        util.rename_field(cr, "account.payment", "end_to_end_id", "end_to_end_uuid")
    else:
        # Create the column here to avoid recomputing for all existing records
        util.create_column(cr, "account_payment", "end_to_end_uuid", "varchar")
