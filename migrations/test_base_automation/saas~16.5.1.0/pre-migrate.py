# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "base.automation.lead.test", "date_action_last", "date_automation_last")
