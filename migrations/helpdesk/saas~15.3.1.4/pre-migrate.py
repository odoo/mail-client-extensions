# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "helpdesk_team", "auto_assignment", "boolean", default=True)
    cr.execute(
        """
           UPDATE helpdesk_team h
              SET auto_assignment=FALSE
            WHERE h.assign_method = 'manual'
        """
    )
    util.change_field_selection_values(cr, "helpdesk.team", "assign_method", {"manual": "randomly"})

    # https://github.com/odoo/enterprise/pull/26832
    util.if_unchanged(cr, "helpdesk.helpdesk_portal_ticket_rule", util.update_record_from_xml)
