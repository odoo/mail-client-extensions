# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "auth_totp_mail.mail_template_totp_invite", util.update_record_from_xml)
