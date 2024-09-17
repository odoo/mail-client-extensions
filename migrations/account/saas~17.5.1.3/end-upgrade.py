from odoo.upgrade import util


def migrate(cr, version):
    # removed in `end` because it is used by `l10n_in` upgrade script.
    util.remove_column(cr, "account_account", "code")
