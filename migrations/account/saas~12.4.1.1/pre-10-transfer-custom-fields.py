# -*- coding: utf-8 -*-
from odoo import modules

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """
    Copy data from custom fields from account.invoice to account.move (lines also).
    Custom fields are defined as `base` fields coming from custom modules as well as
    all manual fields.

    Store fields' definition (as the model will be dropped in end-20-transfer-custom-fields.py)
    and use them in end-20-transfer-custom-fields.py when the link invoice<->move is available.
    """

    cr.execute(
        """
        CREATE TABLE mig_s124_customaccountfieldstotransfer (
            name varchar,
       src_model varchar,
       dst_model varchar,
           store boolean,
           ttype varchar
       )
        """
    )

    src_models = ("account.invoice", "account.invoice.line")

    standard_modules = set(modules.get_modules()) - {"studio_customization", "__export__", "__cloc_exclude__"}

    ands = """
                m.model IN %(src_models)s AND
                f.name NOT IN (
                  SELECT f2.name
                    FROM ir_model_fields f2
              INNER JOIN ir_model m2 ON f2.model_id = m2.id
                   WHERE m2.model = REPLACE(m.model, 'invoice', 'move')
               )
                """
    cr.execute(
        f"""
            INSERT INTO mig_s124_customaccountfieldstotransfer (name, src_model, dst_model, store, ttype)
            -- First obtain custom fields coming from custom modules
            SELECT f.name, m.model, REPLACE (m.model, 'invoice', 'move'), f.store, f.ttype
              FROM ir_model_fields f
              JOIN ir_model m
                ON f.model_id = m.id
              JOIN ir_model_data d
                ON d.res_id = f.id
               AND d.model = 'ir.model.fields'
             WHERE d.module NOT IN %(standard_modules)s
               AND f.state = 'base' -- Redundant, but better to be explicit
               AND {ands}
            -- Second, UNION adds manual fields created directly through UI or with `studio_customization`
             UNION
            SELECT f.name, m.model, REPLACE(m.model, 'invoice', 'move'), f.store, f.ttype
              FROM ir_model_fields f
              JOIN ir_model m ON f.model_id = m.id
             WHERE f.state = 'manual'
               AND {ands}
            """,
        {"src_models": src_models, "standard_modules": tuple(standard_modules)},
    )

    cr.execute("SELECT * FROM mig_s124_customaccountfieldstotransfer")
    for name, src_model, dst_model, store, ttype in cr.fetchall():
        src_table = util.table_of_model(cr, src_model)
        dst_table = util.table_of_model(cr, dst_model)
        if (
            util.column_exists(cr, src_table, name)
            and not util.column_exists(cr, dst_table, name)
            and store
            and ttype != "many2many"
        ):
            util.create_column(cr, dst_table, name, util.column_type(cr, src_table, name))
        else:
            cr.execute(
                """
                        DELETE FROM mig_s124_customaccountfieldstotransfer
                         WHERE name = %s
                           AND src_model = %s
                           AND dst_model = %s
                           """,
                [name, src_model, dst_model],
            )

    cr.execute(
        """
            -- Update the `name` of the `ir.model.data` entry
            UPDATE ir_model_data d
               SET name = 'field_' || fieldstotransfer.dst_model || '__' || fieldstotransfer.name
              FROM mig_s124_customaccountfieldstotransfer fieldstotransfer
              JOIN ir_model_fields f
                ON f.name = fieldstotransfer.name
               AND f.model = fieldstotransfer.src_model
             WHERE f.id = d.res_id
               AND d.model = 'ir.model.fields';

            -- Update `model` and `model_id` of the `ir.model.fields` entry
            UPDATE ir_model_fields f
               SET model = fieldstotransfer.dst_model,
                   model_id = m.id
              FROM mig_s124_customaccountfieldstotransfer fieldstotransfer
              JOIN ir_model m
                ON m.model = fieldstotransfer.dst_model
             WHERE f.model = fieldstotransfer.src_model
               AND f.name = fieldstotransfer.name
                """
    )
