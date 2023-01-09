# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
            UPDATE helpdesk_stage
                SET fold=true
              WHERE is_close=true AND fold=false
        """
    )
    util.update_field_references(cr, "is_close", "fold", only_models=("helpdesk.stage",))
    util.remove_field(cr, "helpdesk.stage", "is_close")

    util.create_column(cr, "helpdesk_team", "ticket_properties", "jsonb")
    util.create_column(cr, "helpdesk_ticket", "properties", "jsonb")
