from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "l10n_in.withhold.wizard", "warning_message")
