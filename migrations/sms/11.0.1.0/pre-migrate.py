# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'res.config.settings', 'default_sms_provider_id')
    cr.execute("DELETE FROM ir_config_parameter WHERE key='default_sms_provider_id'")

    util.remove_model(cr, 'sms.provider')
    util.remove_model(cr, 'sms.message.send')
