# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("10.saas~18"):
        # Should have been removed in saas~18...
        util.remove_constraint(cr, "res_partner_title", "res_partner_title_name_uniq")

    # forgotten temporary table
    cr.execute("DROP TABLE IF EXISTS saas124_acc_mig_bad_mappings")

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
        for model, name in cr.fetchall():
            table = util.table_of_model(cr, model)
            if not util.column_exists(cr, table, name):
                continue
            cr.execute(
                """
                ALTER TABLE {table}
                ALTER COLUMN "{name}"
                 TYPE varchar
                USING CONVERT_FROM("{name}",'UTF8')
            """.format(
                    **locals()
                ),
            )
