# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def _get_model_id(cr, model):
    cr.execute("SELECT id FROM ir_model WHERE model=%s", (model,))
    return cr.fetchone()[0]


def migrate(cr, version):
    cr.execute(
        """
        SELECT name, ttype, src_model, dst_model, state
          FROM mig_s124_accountfieldstotransfer
         WHERE ttype='custom' or state='manual'
        """
    )
    for field, type, src_model, dst_model, state in cr.fetchall():
        src_table = util.table_of_model(cr, src_model)
        dst_table = util.table_of_model(cr, dst_model)
        if state == "manual":
            cr.execute(
                "UPDATE ir_model_fields SET model=%s, model_id=%s WHERE model=%s AND name=%s RETURNING id",
                (dst_model, _get_model_id(cr, dst_model), src_model, field),
            )
        if (
            type != "many2many"
            and util.column_exists(cr, src_table, field)
            and not util.column_exists(cr, dst_table, field)
        ):
            util.create_column(cr, dst_table, field, util.column_type(cr, src_table, field))
            cr.execute(
                "UPDATE mig_s124_accountfieldstotransfer SET transfer=TRUE WHERE name=%s AND src_model=%s AND dst_model=%s",
                (field, src_model, dst_model),
            )
