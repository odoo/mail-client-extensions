# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("UPDATE ir_cron SET interval_type='days' WHERE interval_type='work_days'")

    util.rename_field(cr, 'ir.cron', 'name', 'cron_name')
    util.create_column(cr, 'ir_cron', 'ir_actions_server_id', 'int4')
    cr.execute("""
        WITH actions AS (
            INSERT INTO ir_act_server (sequence, name, type, usage, model_id, model_name, state, code)
                 SELECT c.id, c.cron_name, 'ir.actions.server', 'ir_cron', m.id, m.model, 'code',
                        'model.' || c.function || COALESCE(c.args, '()')
                   FROM ir_cron c
                   JOIN ir_model m ON (m.model = c.model)
              RETURNING id as act_id, sequence as cron_id
        )
        UPDATE ir_cron c
           SET ir_actions_server_id = a.act_id
          FROM actions a
         WHERE a.cron_id = c.id
    """)
    cr.execute("""
        UPDATE ir_act_server s
           SET sequence = c.priority
          FROM ir_cron c
         WHERE s.id = c.ir_actions_server_id
    """)

    util.rename_xmlid(cr, 'base.ir_cron_view', 'base.ir_cron_view_form')
