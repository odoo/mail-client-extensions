# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "web_enterprise.download_contact")
    util.remove_view(cr, "web_enterprise.res_config_settings_view_form")
