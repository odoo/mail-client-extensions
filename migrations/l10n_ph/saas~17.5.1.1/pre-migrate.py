from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "l10n_ph_2307.wizard", "generate_xls_file", "xls_file")
