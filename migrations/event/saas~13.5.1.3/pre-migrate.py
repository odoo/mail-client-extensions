# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_config_settings", "module_website_event_meet", "boolean")
    util.create_column(cr, "res_config_settings", "module_website_event_track_live", "boolean")
    util.create_column(cr, "res_config_settings", "module_website_event_track_quiz", "boolean")
    util.create_column(cr, "res_config_settings", "module_website_event_track_exhib", "boolean")
