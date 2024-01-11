# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "mail.mail_channel_rule")
    infix = "member" if util.version_gte("16.0") else "partner"
    util.update_record_from_xml(cr, f"mail.ir_rule_mail_channel_{infix}_group_user")
