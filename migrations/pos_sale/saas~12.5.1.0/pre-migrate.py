# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "pos_order", "crm_team_id", "int4")
    cr.execute(
        """
        UPDATE pos_order o
           SET crm_team_id = c.crm_team_id
          FROM pos_session s, pos_config c
         WHERE s.id = o.session_id
           AND c.id = s.config_id
    """
    )
