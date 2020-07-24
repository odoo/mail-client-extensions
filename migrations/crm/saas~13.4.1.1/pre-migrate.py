# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "crm.lead", "partner_address_email")
    util.remove_view(cr, "crm.assets_tests")

    util.update_record_from_xml(cr, "crm.digest_tip_crm_0")
    util.update_record_from_xml(cr, "crm.digest_tip_crm_1")
    util.update_record_from_xml(cr, "crm.digest_tip_crm_2")

    # copy opportunity_id on recurrent events
    cr.execute(
        """
        WITH events AS (
            SELECT e.id, b.opportunity_id
              FROM calendar_event e
              JOIN calendar_recurrence r ON r.id = e.recurrence_id
              JOIN calendar_event b ON b.id = r.base_event_id
             WHERE b.opportunity_id IS NOT NULL
               AND e.opportunity_id IS NULL
        )
        UPDATE calendar_event e
           SET opportunity_id = c.opportunity_id
          FROM events c
         WHERE c.id = c.id
    """
    )

    records = util.splitlines(
        """
        relate_partner_opportunities_kanban
        relate_partner_opportunities_tree
        relate_partner_opportunities
    """
    )
    for record in records:
        util.remove_record(cr, f"crm.{record}")
