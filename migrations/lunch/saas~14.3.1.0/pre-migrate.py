# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, 'lunch.ir_cron_lunch')
    util.remove_record(cr, 'lunch.ir_cron_lunch_alerts')
    util.create_column(cr, 'lunch_alert', 'cron_id', 'int4')
    util.create_column(cr, 'lunch_supplier', 'cron_id', 'int4')

    root = util.ref(cr, 'base.user_root')
    query = """
        WITH ir_model_cte AS (
            SELECT id, name
              FROM ir_model
             WHERE model=%s
        ),
        ir_act_server_cte AS (
            INSERT INTO ir_act_server (
                            name, usage, state, model_id, code, type,
                            binding_type, activity_user_type
                        )
                 SELECT 'Lunch: new cron for ' || imcte.name, 'ir_cron', 'code',
                        imcte.id, '', 'ir.actions.server', 'action', 'specific'
                   FROM {table}, ir_model_cte as imcte
              RETURNING id
        ),
        ir_cron_cte AS (
            INSERT INTO ir_cron (
                            ir_actions_server_id, user_id, active, interval_type,
                            interval_number, numbercall, nextcall, doall, priority
                        )
                 SELECT "id", %s, false, 'days', 1, -1, now() at time zone 'UTC', false, 5
                   FROM ir_act_server_cte
              RETURNING id
        ),
        zip_join_cte AS (
            SELECT c.id as cid, t.id as tid
            FROM (SELECT id, row_number() OVER () as rn FROM ir_cron_cte) c
            JOIN (SELECT id, row_number() OVER () as rn FROM {table}) t
            USING (rn)
        )
        UPDATE {table} t
           SET cron_id = z.cid
          FROM zip_join_cte z
         WHERE t.id = z.tid
    """
    rename_fields = {
        'recurrency_monday': 'mon',
        'recurrency_tuesday': 'tue',
        'recurrency_wednesday': 'wed',
        'recurrency_thursday': 'thu',
        'recurrency_friday': 'fri',
        'recurrency_saturday': 'sat',
        'recurrency_sunday': 'sun',
    }
    for model in ('lunch.alert', 'lunch.supplier'):
        table = util.table_of_model(cr, model)
        cr.execute(query.format(table=table), (model, root))
        for old_name, new_name in rename_fields.items():
            util.rename_field(cr, model, old_name, new_name)
