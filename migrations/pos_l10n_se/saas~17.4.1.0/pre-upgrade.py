from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.tax", "sweden_identification_letter")
