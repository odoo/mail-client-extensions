from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(
        cr,
        "account.batch.payment",
        "account_online_linked",
        "account_online_link_payments_enabled",
    )
