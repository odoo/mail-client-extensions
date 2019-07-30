# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.recompute_fields(cr, "crm.lead", ["phone_state", "email_state"])
