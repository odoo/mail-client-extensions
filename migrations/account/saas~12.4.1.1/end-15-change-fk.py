# -*- coding: utf-8 -*-
import logging

from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.account.saas-12.4." + __name__)


def _get_model_id(cr, model):
    cr.execute("SELECT id FROM ir_model WHERE model=%s", [model])
    return cr.fetchone()[0]


def fix_fk(cr, target, update_query):
    new_target = target.replace("invoice", "move")

    for table, column, constraint_name, delete_action in util.get_fk(cr, target, quote_ident=False):
        # Skip some already fixed fields
        if column.endswith("_mig_s124"):
            old_column = column
            column = old_column[:-9]
            _logger.info("Fix %s FK on %s.%s", target, table, column)

            if util.column_exists(cr, table, "id"):
                util.parallel_execute(cr, util.explode_query(cr, update_query.format_map(locals()), alias="t"))
            else:
                cr.execute(update_query.format_map(locals()))

            util.remove_column(cr, table, old_column)

            other_columns = util.get_columns(cr, table, ignore=(column,))
            is_m2m = len(other_columns) == 1

            if not is_m2m:
                delete_action = {
                    "a": "NO ACTION",
                    "r": "RESTRICT",
                    "c": "CASCADE",
                    "n": "SET NULL",
                    "d": "SET DEFAULT",
                }[delete_action]

                cr.execute(
                    f"""
                    ALTER TABLE "{table}"
                      ADD CONSTRAINT "{constraint_name}"
                      FOREIGN KEY ("{column}")
                      REFERENCES "{new_target}"
                      ON DELETE {delete_action};
                """
                )
            else:
                other_column = other_columns[0]
                fk2 = util.target_of(cr, table, other_column)
                if fk2:
                    util.fixup_m2m(cr, table, new_target, fk2[0], column, other_column)


def fix_indirect(cr):

    # Delete duplicated followers:
    cr.execute(
        """
        DELETE
          FROM mail_followers
         WHERE id IN (SELECT m.id
                        FROM mail_followers m
                  INNER JOIN account_invoice i ON m.res_id=i.id
                         AND m.res_model='account.invoice'
                  INNER JOIN mail_followers m2 ON i.move_id=m2.res_id
                         AND (m.partner_id=m2.partner_id OR m.channel_id=m2.channel_id)
                         AND m2.res_model='account.move'
         )
    """
    )

    for ir in util.indirect_references(cr):
        _logger.info("Fix indirect %s", ir.table)
        if ir.table and ir.res_id and ir.res_model:
            util.parallel_execute(
                cr,
                util.explode_query(
                    cr,
                    """
                UPDATE %(table)s d
                   SET %(id_field)s=i.move_id,
                       %(model_field)s='account.move'
                  FROM account_invoice i
                 WHERE i.id=d.%(id_field)s
                   AND d.%(model_field)s='account.invoice'
                   AND i.move_id IS NOT NULL
                    """
                    % {"table": ir.table, "id_field": ir.res_id, "model_field": ir.res_model},
                    alias="d",
                ),
            )
            if util.table_exists(cr, "invl_aml_mapping"):
                util.parallel_execute(
                    cr,
                    util.explode_query(
                        cr,
                        """
                    UPDATE %(table)s d
                       SET %(id_field)s=i.aml_id,
                           %(model_field)s='account.move.line'
                      FROM invl_aml_mapping i
                     WHERE i.invl_id=d.%(id_field)s
                       AND %(model_field)s='account.invoice.line'
                       AND i.aml_id IS NOT NULL
                        """
                        % {"table": ir.table, "id_field": ir.res_id, "model_field": ir.res_model},
                        alias="d",
                    ),
                )
            # if is_account_voucher_installed:
            #     cr.execute(
            #         """
            #         UPDATE %(table)s d
            #            SET %(model_field)s = 'account.move'
            #           FROM account_voucher inv
            #          WHERE %(model_field)s = 'account.voucher'
            #            AND inv.move_id=d.%(id_field)s
            #         """
            #         % {"table": ir.table, "id_field": ir.res_id, "model_field": ir.res_model}
            #     )

    cr.execute(
        """
            UPDATE ir_translation d
               SET res_id = i.move_id,
                    name = replace(d.name, 'account.invoice,', 'account.move,')
              FROM account_invoice i
             WHERE i.id = d.res_id
               AND d.type = 'model'
               AND d.name LIKE 'account.invoice,%'
               AND i.move_id IS NOT NULL
               AND NOT EXISTS( --avoid ir_translation_model_unique
                       SELECT *
                         FROM ir_translation d2
                        WHERE d2.res_id = i.move_id
                          AND d2.name = replace(d.name, 'account.invoice,', 'account.move,')
                          AND d2.type = 'model'
                          AND d2.lang = d.lang
                   )
        """
    )
    if util.table_exists(cr, "invl_aml_mapping"):
        cr.execute(
            """
                UPDATE ir_translation d
                   SET res_id = i.aml_id,
                       name = replace(d.name, 'account.invoice.line,', 'account.move.line,')
                  FROM invl_aml_mapping i
                 WHERE i.invl_id = d.res_id
                   AND d.type = 'model'
                   AND d.name LIKE 'account.invoice.line,%'
                   AND i.aml_id IS NOT NULL
                   AND NOT EXISTS( --avoid ir_translation_model_unique
                       SELECT *
                         FROM ir_translation d2
                        WHERE d2.res_id = i.aml_id
                          AND d2.name = replace(d.name, 'account.invoice.line,', 'account.move.line,')
                          AND d2.type = 'model'
                          AND d2.lang = d.lang
                   )
            """
        )
    # Cleanup remaining: translations to invoices or lines no longer existing.
    cr.execute("DELETE FROM ir_translation WHERE type = 'model' AND name LIKE 'account.invoice,%'")
    cr.execute("DELETE FROM ir_translation WHERE type = 'model' AND name LIKE 'account.invoice.line,%'")

    # "model-comma" fields
    cr.execute(
        """
        SELECT model, name
          FROM ir_model_fields
         WHERE ttype='reference'
    """
    )
    for model, column in cr.fetchall():
        table = util.table_of_model(cr, model)
        if util.column_updatable(cr, table, column):
            util.parallel_execute(
                cr,
                util.explode_query(
                    cr,
                    """
                    UPDATE "{table}" d
                       SET "{column}"='account.move,' || i.move_id
                      FROM account_invoice i
                     WHERE d."{column}" = 'account.invoice,' || i.id
                       AND i.move_id IS NOT NULL
                    """.format(
                        table=table, column=column
                    ),
                    alias="d",
                ),
            )
            if util.table_exists(cr, "invl_aml_mapping"):
                util.parallel_execute(
                    cr,
                    util.explode_query(
                        cr,
                        """
                        UPDATE "{table}" d
                           SET "{column}"='account.move.line,' || i.aml_id
                          FROM invl_aml_mapping i
                         WHERE d."{column}" = 'account.invoice.line,' || i.invl_id
                           AND i.aml_id IS NOT NULL
                        """.format(
                            table=table, column=column
                        ),
                        alias="d",
                    ),
                )


def fix_custom_m2o(cr):
    for target_model, source_model in [
        ("account.move", "account.invoice"),
        ("account.move.line", "account.invoice.line"),
    ]:
        _logger.info("Fix custom M2O %s", source_model)
        cr.execute(
            """
            UPDATE ir_model_fields
               SET relation=%s
             WHERE ttype in ('many2one', 'many2many')
               AND relation=%s
               AND state='manual'
        """,
            [target_model, source_model],
        )


def migrate(cr, version):
    fix_fk(
        cr,
        "account_invoice",
        """
            UPDATE "{table}" t
               SET "{column}" = i.move_id
              FROM account_invoice i
             WHERE i.id = t."{old_column}"
        """,
    )

    fix_fk(
        cr,
        "account_invoice_line",
        """
            UPDATE "{table}" t
               SET "{column}" = l.aml_id
              FROM invl_aml_mapping l
             WHERE l.invl_id = t."{old_column}"
        """,
    )

    fix_indirect(cr)
    fix_custom_m2o(cr)

    for table in [("account.invoice", "account.move"), ("account.invoice.line", "account.move.line")]:
        cr.execute(
            "UPDATE ir_rule SET model_id=%s WHERE model_id=%s",
            [_get_model_id(cr, table[1]), _get_model_id(cr, table[0])],
        )
