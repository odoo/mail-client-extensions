# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sign.sign_template_mail_follower")

    util.create_column(cr, "sign_request", "message", "text")
    util.create_column(cr, "sign_request", "message_cc", "text")
    util.create_column(cr, "sign_send_request", "message_cc", "text")
