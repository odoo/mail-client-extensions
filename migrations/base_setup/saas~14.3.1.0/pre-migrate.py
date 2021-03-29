# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "res.config.settings", "module_mail_client_extension", "crm", "base_setup")
    util.rename_field(cr, "res.config.settings", "module_mail_client_extension", "module_mail_plugin")
    util.remove_field(cr, "res.config.settings", "paperformat_id")
