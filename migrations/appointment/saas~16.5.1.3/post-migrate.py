# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE appointment_type
        SET booked_mail_template_id=%s,
            canceled_mail_template_id=%s
    """,
        [
            util.ref(cr, "appointment.attendee_invitation_mail_template"),
            util.ref(cr, "appointment.appointment_canceled_mail_template"),
        ],
    )
