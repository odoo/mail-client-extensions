# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'helpdesk_team', 'use_credit_notes')
    util.create_column(cr, 'helpdesk_team', 'use_coupons')
    util.create_column(cr, 'helpdesk_team', 'use_product_returns')
    util.create_column(cr, 'helpdesk_team', 'use_product_repairs')

    util.create_column(cr, 'helpdesk_ticket', 'email_cc', 'varchar')
