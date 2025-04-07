from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "bank.rec.widget")
    util.remove_model(cr, "bank.rec.widget.line")
    util.remove_view(cr, "account_accountant.view_account_move_line_search_bank_rec_widget")
