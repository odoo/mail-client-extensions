# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sign_request_item", "mail_sent_order", "int4", default=1)
    util.create_column(cr, "sign_send_request", "set_sign_order", "boolean")
    util.create_column(cr, "res_config_settings", "group_show_sign_order", "boolean")
