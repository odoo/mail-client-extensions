# -*- coding: utf-8 -*-
import json

try:
    from odoo.tools import pickle as _pickle
except ImportError:
    import pickle as _pickle

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # actions
    util.remove_field(cr, "ir.actions.server", "menu_ir_values_id")
    util.remove_field(cr, "ir.actions.report", "ir_values_id")
    util.create_column(cr, "ir_actions", "binding_model_id", "int4")
    util.create_column(cr, "ir_actions", "binding_type", "varchar")

    col, _ = util.helpers._ir_values_value(cr, prefix="v")

    cr.execute(
        """
        WITH act_multi AS (
            SELECT id, bool_or(multi) as multi FROM (
                SELECT id, multi FROM ir_act_window
                 UNION
                SELECT id, multi FROM ir_act_report_xml
                 UNION
                SELECT id, false FROM ir_actions
            ) u
            GROUP BY id
        )
        UPDATE ir_actions a
           SET binding_model_id = m.id,
               binding_type = CASE WHEN v.key2 = 'client_print_multi' THEN 'report'
                                   WHEN NOT u.multi AND v.key2 = 'client_action_relate' THEN 'action_form_only'
                                   ELSE 'action'
                               END
          FROM act_multi u, ir_values v, ir_model m
         WHERE u.id = a.id
           AND v.key = 'action'
           AND a.id = CASE
                           -- ir.actions.actions(354,)
                           WHEN {col} like '%,)' THEN NULLIF(split_part(split_part({col}, '(', 2), ',', 1), '')::int4
                           -- ir.actions.act_window,167
                           ELSE NULLIF(split_part({col}, ',', 2), '')::int4
                      END
           AND m.model = v.model
    """.format(
            col=col
        )
    )

    # default
    pv = util.parse_version
    if pv(version) < pv("10.saas~14"):
        crm = util.import_script("crm/10.saas~14.1.0/pre-settings.py")
        crm.migrate(cr, version)

    cr.execute("DROP TABLE IF EXISTS ir_default")  # just in case
    cr.execute("DROP SEQUENCE IF EXISTS ir_default_id_seq")  # just in previous case
    cr.execute(
        """
        CREATE TABLE ir_default (
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            field_id integer,
            user_id integer,
            company_id integer,
            condition varchar,
            json_value varchar
        )
    """
    )

    if util.column_type(cr, "ir_values", "value") == "bytea":

        def encode(x):
            return bytes(int(x, 16) for x in util.chunks(x[2:], 2))

    else:

        def encode(x):
            return x.encode("utf8")

    def pickle(x):
        return _pickle.loads(encode(x), encoding="utf-8")

    cr.execute(
        """
        INSERT INTO ir_default(create_uid, create_date, write_uid, write_date,
                               field_id, user_id, company_id, condition, json_value)
             SELECT v.create_uid, v.create_date, v.write_uid, v.write_date,
                    f.id, v.user_id, v.company_id, v.key2, v.value
               FROM ir_values v
               JOIN ir_model_fields f ON (f.model = v.model AND f.name = v.name)
              WHERE v.key = 'default'
          RETURNING id, json_value
    """
    )
    for did, rick in cr.fetchall():
        value = pickle(rick)  # hum
        cr.execute("UPDATE ir_default SET json_value=%s WHERE id=%s", [json.dumps(value), did])

    util.remove_model(cr, "ir.values")
