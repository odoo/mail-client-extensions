# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    rt = dict(reset_translations={"body"})
    util.if_unchanged(cr, "event_sms.sms_template_data_event_registration", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "event_sms.sms_template_data_event_reminder", util.update_record_from_xml, **rt)
