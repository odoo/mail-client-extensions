from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "marketing_card.module_category_marketing_card")
    util.update_record_from_xml(cr, "marketing_card.marketing_card_group_user")
    util.update_record_from_xml(cr, "marketing_card.marketing_card_group_manager")
