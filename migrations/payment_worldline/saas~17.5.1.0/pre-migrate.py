from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "payment.provider", "ogone_pspid", "worldline_pspid")
    util.rename_field(cr, "payment.provider", "ogone_userid", "worldline_api_key")
    util.rename_field(cr, "payment.provider", "ogone_password", "worldline_api_secret")
    util.remove_field(cr, "payment.provider", "ogone_shakey_in")
    util.remove_field(cr, "payment.provider", "ogone_shakey_out")
    util.remove_field(cr, "payment.provider", "ogone_hash_function")
