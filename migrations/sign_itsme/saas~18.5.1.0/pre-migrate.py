from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "sign_itsme.sign_item_role_itsme_customer", keep_xmlids=False)
