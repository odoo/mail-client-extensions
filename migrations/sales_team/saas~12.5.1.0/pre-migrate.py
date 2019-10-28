# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "crm_team", "sequence", "int4")
    util.remove_field(cr, "crm.team", "reply_to")
    cr.execute(
        """
        WITH seq AS (
            SELECT id, row_number() OVER(ORDER BY name) seq
              FROM crm_team
        )
        UPDATE crm_team t
           SET sequence = seq.seq
          FROM seq
         WHERE t.id = seq.id
    """
    )
