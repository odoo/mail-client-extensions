# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "sms.sms_template_demo_0", util.update_record_from_xml)
