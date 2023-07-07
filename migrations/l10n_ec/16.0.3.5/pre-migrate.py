from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_ec.ec110502")
