# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("12.0", "saas~16.4"):
        # server actions associated to automated actions should have xmlids
        cr.execute(
            """
            INSERT INTO ir_model_data(
                   module, name,
                   model, res_id, noupdate,
                   create_uid, write_uid, create_date, write_date)
            SELECT bd.module, bd.name || '_ir_actions_server',
                   'ir.actions.server', b.action_server_id, bd.noupdate,
                   bd.create_uid, bd.write_uid, bd.create_date, bd.write_date
              FROM base_automation b
              JOIN ir_model_data bd
                ON bd.model = 'base.automation'
               AND bd.res_id = b.id
         LEFT JOIN ir_model_data ad
                ON ad.model = 'ir.actions.server'
               AND ad.res_id = b.action_server_id
             WHERE ad.id IS NULL
            """,
        )
