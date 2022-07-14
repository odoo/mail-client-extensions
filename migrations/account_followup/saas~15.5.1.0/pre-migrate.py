# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "account.report.manager", "partner_id")
    util.remove_field(cr, "account.report.manager", "email_subject")
