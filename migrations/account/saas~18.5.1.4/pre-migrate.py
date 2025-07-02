from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, model="res.partner", fieldname="duplicated_bank_account_partners_count")
