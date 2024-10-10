from odoo.upgrade import util


def migrate(cr, version):
    for name in ("account_online_sync_link_rule", "account_online_sync_account_rule"):
        util.if_unchanged(cr, f"account_online_synchronization.{name}", util.update_record_from_xml)
