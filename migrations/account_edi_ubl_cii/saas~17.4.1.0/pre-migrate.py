from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move.send", "ubl_partner_warning")
    util.remove_field(cr, "account.move.send", "show_ubl_company_warning")
