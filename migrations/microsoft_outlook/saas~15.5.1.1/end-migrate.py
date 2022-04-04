# -*- coding:utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "microsoft.outlook.mixin", "use_microsoft_outlook_service")
