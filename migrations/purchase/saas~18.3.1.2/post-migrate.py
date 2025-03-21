from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "purchase.portal_purchase_order_user_rule", util.update_record_from_xml)
    util.if_unchanged(cr, "purchase.portal_purchase_order_line_rule", util.update_record_from_xml)
