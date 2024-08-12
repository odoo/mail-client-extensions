from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move.line", "l10n_pe_group_id")
