from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "website_slides.slide_template_published", util.update_record_from_xml)
    util.if_unchanged(cr, "website_slides.slide_template_shared", util.update_record_from_xml)
    util.if_unchanged(cr, "website_slides.mail_template_channel_completed", util.update_record_from_xml)
    util.if_unchanged(cr, "website_slides.mail_template_channel_shared", util.update_record_from_xml)
