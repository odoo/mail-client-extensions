from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "website_sale_collect.product_pick_up_in_store", util.update_record_from_xml)
    util.if_unchanged(cr, "website_sale_collect.carrier_pick_up_in_store", util.update_record_from_xml)
