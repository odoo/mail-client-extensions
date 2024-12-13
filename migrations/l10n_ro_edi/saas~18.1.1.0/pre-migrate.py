from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "l10n_ro_edi_oauth_error")
    util.remove_field(cr, "res.config.settings", "l10n_ro_edi_oauth_error")
