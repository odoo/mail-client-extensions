# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_config_settings", "jitsi_server_domain", "varchar")
