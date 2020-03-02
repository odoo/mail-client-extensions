# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, 'utm.campaign', 'mailing_clicks_ratio')
    util.remove_field(cr, 'utm.campaign', 'mailing_items')
    util.remove_field(cr, 'utm.campaign', 'mailing_clicked')
    util.remove_field(cr, 'utm.campaign', 'total')
    util.remove_field(cr, 'utm.campaign', 'scheduled')
    util.remove_field(cr, 'utm.campaign', 'failed')
    util.remove_field(cr, 'utm.campaign', 'ignored')
    util.remove_field(cr, 'utm.campaign', 'sent')
    util.remove_field(cr, 'utm.campaign', 'delivered')
    util.remove_field(cr, 'utm.campaign', 'opened')
    util.remove_field(cr, 'utm.campaign', 'replied')
    util.remove_field(cr, 'utm.campaign', 'bounced')
