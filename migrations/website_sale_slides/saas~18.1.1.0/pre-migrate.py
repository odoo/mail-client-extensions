from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "website_sale_slides.product_category_courses")
