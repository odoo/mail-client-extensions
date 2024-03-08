from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "sale_product_configurator", "sale")
    util.merge_module(cr, "pos_sale_product_configurator", "pos_sale")
    util.merge_module(cr, "website_sale_product_configurator", "website_sale")

    if util.has_enterprise():
        util.merge_module(cr, "website_sale_renting_product_configurator", "website_sale_renting")
    util.force_upgrade_of_fresh_module(cr, "hr_homeworking_calendar")
