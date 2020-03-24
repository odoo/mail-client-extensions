# -*- coding: utf-8 -*-
import logging

from odoo.addons.base.maintenance.migrations import util


_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.account.saas-12.4." + __name__)


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
        SELECT name, ttype, src_model, dst_model, transfer
          FROM mig_s124_accountfieldstotransfer
         WHERE ttype='custom' or state='manual'
        """
    )
    for field, type, src_model, dst_model, transfer in cr.fetchall():
        src_table = util.table_of_model(cr, src_model)
        dst_table = util.table_of_model(cr, dst_model)
        if transfer:
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

    cr.execute(
        """
        UPDATE "account_move_line" aml
           SET sequence=inv.sequence
          FROM "account_invoice_line" inv
          JOIN invl_aml_mapping map ON map.invl_id=inv.id
         WHERE aml.id = map.aml_id
    """
    )
    is_account_voucher_installed = util.table_exists(cr, "account_voucher")

    # Models
    # You may think that the following query is the same as the one in `util.get_fk()`
    # But no. There is a subtle change. It actually get the FKs *of* a table (all many2one of a table)
    q = """SELECT quote_ident(cl1.relname) as table,
                  quote_ident(con.conname) as conname
             FROM pg_constraint as con, pg_class as cl1, pg_class as cl2,
                  pg_attribute as att1, pg_attribute as att2
            WHERE con.conrelid = cl1.oid
              AND con.confrelid = cl2.oid
              AND array_lower(con.conkey, 1) = 1
              AND con.conkey[1] = att1.attnum
              AND att1.attrelid = cl1.oid
              AND cl1.relname = %s
              AND att2.attname = 'id'
              AND array_lower(con.confkey, 1) = 1
              AND con.confkey[1] = att2.attnum
              AND att2.attrelid = cl2.oid
              AND con.contype = 'f'
    """

    for model in ["account.invoice.tax", "account.invoice.line", "account.invoice"]:
        util.remove_model(cr, model, drop_table=False)
        for constraint in util.get_fk(cr, util.table_of_model(cr, model)):
            cr.execute("ALTER TABLE %s DROP CONSTRAINT %s" % (constraint[0], constraint[2]))

        cr.execute(q, (util.table_of_model(cr, model),))
        for rec in cr.fetchall():
            cr.execute("ALTER TABLE %s DROP CONSTRAINT %s" % (rec[0], rec[1]))

    util.remove_model(cr, "account.register.payments")
    if is_account_voucher_installed:
        util.remove_model(cr, "account_voucher", drop_table=False)
        util.remove_model(cr, "account_voucher_line", drop_table=False)
