from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "l10n_in.withhold.wizard", "withhold_line_ids")
    util.remove_model(cr, "l10n_in.withhold.wizard.line")
    util.remove_field(cr, "account.move", "l10n_in_tcs_tds_warning")
