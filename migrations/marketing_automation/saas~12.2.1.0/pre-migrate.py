# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, 'marketing.activity', 'domain', 'activity_domain')
    util.create_column(cr, 'marketing_activity', 'domain', 'varchar')
