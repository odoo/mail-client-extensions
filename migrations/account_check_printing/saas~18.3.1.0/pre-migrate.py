from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_accountant_check_printing.view_account_move_line_search_bank_rec_widget")
