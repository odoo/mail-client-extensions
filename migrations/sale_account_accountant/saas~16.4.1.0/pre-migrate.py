from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_account_accountant.view_bank_rec_widget_form_inherit_sale_order")
