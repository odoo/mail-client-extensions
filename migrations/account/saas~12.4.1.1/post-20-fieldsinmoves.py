# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def _get_linking(table):
    if table == "account_invoice":
        return "WHERE am.id = inv.move_id"
    return "INNER JOIN invl_aml_mapping map ON map.invl_id=inv.id WHERE am.id = map.aml_id"


def _get_model_id(cr, model):
    cr.execute("SELECT id FROM ir_model WHERE model=%s", (model,))
    return cr.fetchone()[0]


def migrate(cr, version):
    cr.execute(
        """
        SELECT name, src_model, dst_model
          FROM mig_s124_accountfieldstotransfer
         WHERE state='manual'
        """
    )
    for field, src_model, dst_model in cr.fetchall():
        cr.execute(
            "UPDATE ir_model_fields SET model=%s, model_id=%s WHERE model=%s AND name=%s RETURNING id",
            (dst_model, _get_model_id(cr, dst_model), src_model, field),
        )
    cr.execute(
        """
        SELECT name, ttype, src_model, dst_model
          FROM mig_s124_accountfieldstotransfer
         WHERE ttype='custom' or state='manual'
        """
    )
    for field, type, src_model, dst_model in cr.fetchall():
        src_table = util.table_of_model(cr, src_model)
        dst_table = util.table_of_model(cr, dst_model)
        if type == "many2many":
            pass
        elif util.column_exists(cr, src_table, field) and not util.column_exists(cr, dst_table, field):
            util.create_column(cr, dst_table, field, util.column_type(cr, src_table, field))
            cr.execute(
                """
                UPDATE "%(dst_table)s" am
                   SET "%(field)s"=inv."%(field)s"
                  FROM "%(src_table)s" inv
                  %(link)s
                """
                % {"dst_table": dst_table, "src_table": src_table, "field": field, "link": _get_linking(src_table)}
            )
    cr.execute("DROP TABLE mig_s124_accountfieldstotransfer")

    is_account_voucher_installed = util.table_exists(cr, "account_voucher")

    # Models
    util.remove_model(cr, "account.invoice.tax", drop_table=False)
    util.remove_model(cr, "account.invoice.line", drop_table=False)
    util.remove_model(cr, "account.invoice", drop_table=False)
    util.remove_model(cr, "account.register.payments")
    if is_account_voucher_installed:
        util.remove_model(cr, "account_voucher", drop_table=False)
        util.remove_model(cr, "account_voucher_line", drop_table=False)
