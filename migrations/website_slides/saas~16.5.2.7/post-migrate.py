from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "website_slides.rule_slide_channel_visibility_signed_in_user", util.update_record_from_xml)
    util.if_unchanged(cr, "website_slides.rule_slide_slide_signed_in_user", util.update_record_from_xml)
    util.if_unchanged(cr, "website_slides.rule_slide_slide_resource_downloadable", util.update_record_from_xml)
