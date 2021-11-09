# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    rt = dict(reset_translations={"subject", "body_html"})

    util.if_unchanged(cr, "appointment.appointment_booked_mail_template", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "appointment.appointment_canceled_mail_template", util.update_record_from_xml, **rt)
