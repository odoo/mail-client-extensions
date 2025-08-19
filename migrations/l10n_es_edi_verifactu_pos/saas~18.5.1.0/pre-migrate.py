from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos.order", "l10n_es_edi_verifactu_show_cancel_button")
