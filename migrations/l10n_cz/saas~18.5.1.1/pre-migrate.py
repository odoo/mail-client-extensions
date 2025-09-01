from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_cz.view_move_form_l10n_cz")
