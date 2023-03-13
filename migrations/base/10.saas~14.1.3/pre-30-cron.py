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
        ), upd_crons AS (
            UPDATE ir_cron c
               SET ir_actions_server_id = a.act_id
              FROM actions a
             WHERE a.cron_id = c.id
         RETURNING c.id, c.ir_actions_server_id
        )
        INSERT INTO ir_model_data(
               module, name,
               model, res_id, noupdate,
               create_uid, write_uid, create_date, write_date)
        SELECT cd.module, cd.name || '_ir_actions_server',
               'ir.actions.server', c.ir_actions_server_id, cd.noupdate,
               cd.create_uid, cd.write_uid, cd.create_date, cd.write_date
          FROM upd_crons c
          JOIN ir_model_data cd
            ON cd.model = 'ir.cron'
           AND cd.res_id = c.id
    """)

    cr.execute("""
        UPDATE ir_act_server s
           SET sequence = c.priority
          FROM ir_cron c
         WHERE s.id = c.ir_actions_server_id
    """)
    cr.execute(
        """
            ALTER TABLE ir_cron 
        ADD FOREIGN KEY (ir_actions_server_id)
             REFERENCES ir_act_server(id) ON DELETE RESTRICT
        """
    )

    # remove cron from unknow models (wont never run)
    cr.execute("DELETE FROM ir_cron WHERE ir_actions_server_id IS NULL")

    for field in 'model function args'.split():
        util.remove_field(cr, 'ir.cron', field)

    util.rename_xmlid(cr, 'base.ir_cron_view', 'base.ir_cron_view_form')
