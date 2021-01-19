# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sign_template", "user_id", "int4")
    cr.execute("UPDATE sign_template SET user_id = create_uid WHERE user_id IS NULL")

    util.create_column(cr, "sign_send_request", "activity_id", "int4")
    util.create_column(cr, "sign_send_request", "has_default_template", "boolean")

    util.create_column(cr, "sign_request_item", "is_mail_sent", "boolean")
    cr.execute("UPDATE sign_request_item SET is_mail_sent = true WHERE state = 'sent'")
