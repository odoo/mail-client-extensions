# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("UPDATE purchase_order SET date_planned = expected_date WHERE date_planned IS NULL")
    util.remove_field(cr, "purchase.order", "expected_date")
    util.create_column(cr, "purchase_order", "mail_reminder_confirmed", "boolean")
    util.create_column(cr, "purchase_order", "mail_reception_confirmed", "boolean")
    util.create_column(cr, "res_config_settings", "group_send_reminder", "boolean")
