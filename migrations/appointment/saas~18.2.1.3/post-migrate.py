from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "appointment.attendee_invitation_mail_template", util.update_record_from_xml)
