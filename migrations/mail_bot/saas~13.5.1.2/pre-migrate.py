# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mail_bot.view_users_form_inherit_mail_notification_alert")
