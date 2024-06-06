from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "sign.sign_item_role_company", "sign.sign_item_role_user")
