# -*- coding: utf-8 -*-
import collections

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("10.saas~18"):
        # Should have been removed in saas~18...
        util.remove_constraint(cr, "res_partner_title", "res_partner_title_name_uniq", warn=False)

    # forgotten temporary table
    cr.execute("DROP TABLE IF EXISTS saas124_acc_mig_bad_mappings")

    if util.version_gte("12.0"):
        # server actions associated to cron jobs should have xmlids
        cr.execute(
            """
            INSERT INTO ir_model_data(
                   module, name,
                   model, res_id, noupdate,
                   create_uid, write_uid, create_date, write_date)
            SELECT cd.module, cd.name || '_ir_actions_server',
                   'ir.actions.server', c.ir_actions_server_id, cd.noupdate,
                   cd.create_uid, cd.write_uid, cd.create_date, cd.write_date
              FROM ir_cron c
              JOIN ir_model_data cd
                ON cd.model = 'ir.cron'
               AND cd.res_id = c.id
         LEFT JOIN ir_model_data ad
                ON ad.model = 'ir.actions.server'
               AND ad.res_id = c.ir_actions_server_id
             WHERE ad.id IS NULL
       ON CONFLICT DO NOTHING
            """,
        )

    if util.version_gte("12.0"):
        cr.execute(
            r"""
               UPDATE ir_model_fields fields
                  SET ttype = 'char'
                 FROM ir_model_fields f
                 JOIN ir_model_data d
                   ON d.res_id = f.id
                  AND d.model = 'ir.model.fields'
                WHERE d.module = 'studio_customization'
                  AND f.state = 'manual'
                  AND f.ttype = 'binary'
                  AND f.name LIKE 'x\_%\_filename'
                  AND fields.id = f.id
            RETURNING fields.model,
                      fields.name
        """
        )
        info = collections.defaultdict(list)
        for model, name in cr.fetchall():
            table = util.table_of_model(cr, model)
            if not util.column_exists(cr, table, name):
                continue
            info[table].append(name)

        queries = [
            "ALTER TABLE {table}\n{alter_columns}".format(
                table=table,
                alter_columns=",\n".join(
                    """
                    ALTER COLUMN "{name}"
                     TYPE varchar
                    USING CONVERT_FROM("{name}",'UTF8')
                    """.format(name=name)
                    for name in names
                ),
            )
            for table, names in info.items()
        ]
        util.parallel_execute(cr, queries)
