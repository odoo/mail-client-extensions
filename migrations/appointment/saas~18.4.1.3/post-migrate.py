from odoo.upgrade import util


def migrate(cr, version):
    rt = {"reset_translations": {"body_html"}}
    util.if_unchanged(cr, "appointment.appointment_booked_mail_template", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "appointment.attendee_invitation_mail_template", util.update_record_from_xml, **rt)
