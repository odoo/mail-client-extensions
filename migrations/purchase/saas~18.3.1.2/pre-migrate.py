from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "purchase.action_purchase_batch_bills")
    util.remove_record(cr, "purchase.res_partner_view_purchase_account_buttons")
