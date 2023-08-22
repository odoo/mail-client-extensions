# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "crm.lead", "calendar_event_count")
    util.rename_field(cr, "crm.lead", "date_action_last", "date_automation_last")
