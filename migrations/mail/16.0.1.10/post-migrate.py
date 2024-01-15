# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "mail.ir_rule_mail_channel_member_group_user")
    util.update_record_from_xml(cr, "mail.mail_channel_rule")
