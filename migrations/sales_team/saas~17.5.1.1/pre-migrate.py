from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "sales_team.ebay_sales_team")
