from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "event_booth.event_booth_category_standard", util.update_record_from_xml)
    util.if_unchanged(cr, "event_booth.event_booth_category_premium", util.update_record_from_xml)
    util.if_unchanged(cr, "event_booth.event_booth_category_vip", util.update_record_from_xml)
