from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_invoice_extract.view_move_form")
