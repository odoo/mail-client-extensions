# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "calendar_sms.sms_template_data_calendar_reminder", util.update_record_from_xml)
