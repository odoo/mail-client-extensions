from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account.view_company_partner_bank_form")
