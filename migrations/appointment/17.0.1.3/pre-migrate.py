# -*- coding: utf-8 -*-
from odoo.upgrade import util
from odoo.upgrade.util import expand_braces as eb


def migrate(cr, version):
    util.rename_xmlid(cr, *eb("appointment.menu_appointment_type_custom{_and_anytime,}"))
    util.rename_xmlid(cr, *eb("appointment.appointment_type_action_custom{_and_anytime,}"))
