# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.upgrade import util


def migrate(cr, version):
    # rename the selection field [trigger_type] 'act' to 'activity'
    cr.execute(
        """
            UPDATE marketing_activity
               SET trigger_type = 'activity'
             WHERE trigger_type = 'act'
        """
    )

    util.remove_field(cr, 'marketing.campaign', 'mailing_clicks_ratio')
    util.remove_field(cr, 'marketing.campaign', 'mailing_items')
    util.remove_field(cr, 'marketing.campaign', 'mailing_clicked')
    util.remove_field(cr, 'marketing.campaign', 'total')
    util.remove_field(cr, 'marketing.campaign', 'scheduled')
    util.remove_field(cr, 'marketing.campaign', 'failed')
    util.remove_field(cr, 'marketing.campaign', 'ignored')
    util.remove_field(cr, 'marketing.campaign', 'sent')
    util.remove_field(cr, 'marketing.campaign', 'delivered')
    util.remove_field(cr, 'marketing.campaign', 'opened')
    util.remove_field(cr, 'marketing.campaign', 'replied')
    util.remove_field(cr, 'marketing.campaign', 'bounced')
