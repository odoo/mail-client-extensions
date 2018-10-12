# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "crm_lead", "won_status", "varchar")
    util.create_column(cr, "crm_lead", "days_to_convert", "float8")
    util.create_column(cr, "crm_lead", "days_exceeding_closing", "float8")

    cr.execute(
        """
        UPDATE crm_lead
           SET won_status = CASE WHEN active = true AND probability = 100 THEN 'won'
                                 WHEN COALESCE(active, false) = false AND probability = 0 THEN 'lost'
                                 ELSE 'pending'
                             END,
               days_to_convert = date_part('days', date_conversion - create_date),
               days_exceeding_closing = date_part('days', date_deadline - date_closed)
    """
    )
