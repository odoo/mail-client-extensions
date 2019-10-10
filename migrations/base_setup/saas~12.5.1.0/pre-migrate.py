# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "module_sms")
    util.remove_field(cr, "res.config.settings", "company_share_partner")
