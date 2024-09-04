from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "marketing_card.card_template_user_image", force_create=False)
    util.if_unchanged(cr, "marketing_card.marketing_card_group_user", util.update_record_from_xml, force_create=False)
