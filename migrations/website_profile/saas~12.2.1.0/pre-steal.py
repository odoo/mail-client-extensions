# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(cr, *util.expand_braces("website_{forum,profile}.verification_email"))
    cr.execute("UPDATE ir_config_parameter SET key = 'website_profile.uuid' WHERE key = 'website_forum.uuid'")
