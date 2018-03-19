# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'res.config.settings', 'default_lang_id', 'website_default_lang_id')
    util.rename_field(cr, 'res.config.settings', 'default_lang_code', 'website_default_lang_code')
