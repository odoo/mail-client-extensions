from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp_subcontracting.mrp_subcontracting_product_template_search_view")
