# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # check activivated settings in order to get 'show_operation' value on picking types
    env = util.env(cr)
    env['res.config.settings'].new().execute()
