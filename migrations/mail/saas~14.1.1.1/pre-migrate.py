# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "mail.email_template_partner")
    util.remove_record(cr, "mail.ir_rule_mail_channel_partner_group_user")
