# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(
        cr, "calendar_sms.sms_message_send_action_multi", "calendar_sms.calendar_event_act_window_sms_composer_single"
    )
