from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_de_pos_cert.dsfinvk_cash_point_closing_template")
