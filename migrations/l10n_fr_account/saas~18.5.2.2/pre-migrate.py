from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "l10n_fr.fec.export.wizard", "exclude_zero")
