# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "module_crm_reveal")
    util.remove_field(cr, "crm.activity.report", "subject")
