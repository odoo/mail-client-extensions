from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_es_edi_tbai.view_move_form")
