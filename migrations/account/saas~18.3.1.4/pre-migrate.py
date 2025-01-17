from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account.portal_my_details_fields")
