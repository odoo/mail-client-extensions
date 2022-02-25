# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("appointment_hr.{calendar_,}appointment_type_view_form_inherit_appointment_hr"))
