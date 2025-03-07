from odoo.upgrade import util

script = util.import_script("product/saas~18.3.1.2/pre-migrate.py")


def migrate(cr, version):
    util.if_unchanged(cr, "purchase.portal_purchase_order_user_rule", util.update_record_from_xml)
    util.if_unchanged(cr, "purchase.portal_purchase_order_line_rule", util.update_record_from_xml)

    script.set_product_manager(cr, "purchase.group_purchase_manager")
