# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # https://github.com/odoo/enterprise/pull/26811
    util.if_unchanged(cr, "helpdesk.helpdesk_portal_ticket_rule", util.update_record_from_xml)
    # https://github.com/odoo/enterprise/pull/31804
    util.if_unchanged(cr, "helpdesk.helpdesk_sla_report_analysis_rule_manager", util.update_record_from_xml)

    util.recompute_fields(cr, "helpdesk.sla.status", ["exceeded_hours"])
    cr.execute(
        """
        WITH ticket_min_hours AS (
            SELECT ticket_id, MIN(exceeded_hours) < 0 as min_hours
              FROM helpdesk_sla_status st
          GROUP BY st.ticket_id
        )
        UPDATE helpdesk_ticket t
           SET sla_reached = tmh.min_hours
          FROM ticket_min_hours tmh
         WHERE tmh.ticket_id = t.id
           AND tmh.min_hours = TRUE
    """
    )
