# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "event_tag", "color", "int4", default=0)
    for suffix in {"meet", "track_live", "track_quiz", "track_exhibitor"}:
        util.create_column(cr, "res_config_settings", f"module_website_event_{suffix}", "boolean")
