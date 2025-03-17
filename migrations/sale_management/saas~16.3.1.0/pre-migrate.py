from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "sale_management.digest_tip_sale1_management_0", noupdate=False)
    util.force_noupdate(cr, "sale_management.digest_tip_sale_management_1", noupdate=False)
