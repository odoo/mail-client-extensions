# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "mail.wizard.invite", "send_mail", "notify")
    util.create_column(cr, "mail_alias", "alias_status", "varchar", default="not_tested")
