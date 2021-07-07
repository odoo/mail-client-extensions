# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "website.configurator.feature", "website_types_preselection", "website_config_preselection")
