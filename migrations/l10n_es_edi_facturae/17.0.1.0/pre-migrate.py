from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "account_move_send", "l10n_es_edi_facturae_checkbox_xml")
