# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    renames = [
        "website_appointment.{calendar_,}appointment_type_rule_public",
        "website_appointment.{calendar_,}appointment_type_view_kanban",
        "website_appointment.{calendar_,}appointment_type_view_form",
        "website_appointment.{calendar_,}appointment_type_view_search",
    ]
    for rename in renames:
        util.rename_xmlid(cr, *eb(rename))
    util.force_noupdate(cr, "website_appointment.appointment_type_rule_public")
