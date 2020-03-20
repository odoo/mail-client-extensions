# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.users", "out_of_office_message")
    util.remove_field(cr, "mail.template", "user_signature")
    util.create_column(cr, "mail_alias", "alias_bounced_content", "text")
    util.remove_model(cr, "mail.address.mixin", drop_table=False)
