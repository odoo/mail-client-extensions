from odoo.upgrade import util


def migrate(cr, version):
    rt = dict(reset_translations={"body_html"})

    util.if_unchanged(cr, "event.event_registration_mail_template_badge", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "event.event_subscription", util.update_record_from_xml, **rt)
