from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "website_sale.row_addresses", "website_sale.address_row")
    util.rename_field(cr, "res.config.settings", "module_website_sale_picking", "module_website_sale_collect")
