from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_sa.view_move_form")
