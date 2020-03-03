# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mail.message", "description")
    util.remove_field(cr, "mail.message", "website_published")
    util.remove_record(cr, "website_mail.mail_message_rule_public")
