from odoo.upgrade import util


def migrate(cr, version):
    op_type1_id = util.ref(cr, "l10n_br_avatax.operation_type_1")
    op_type3_id = util.ref(cr, "l10n_br_avatax.operation_type_3")
    op_type60_id = util.ref(cr, "l10n_br_avatax.operation_type_60")
    for inh in util.for_each_inherit(cr, "account.external.tax.mixin"):
        table = util.table_of_model(cr, inh.model)
        if util.table_exists(cr, table):
            util.explode_execute(
                cr,
                cr.mogrify(
                    util.format_query(
                        cr,
                        """
                        WITH _is_avatax AS (
                            SELECT t.id
                              FROM {table} t
                              JOIN res_company company
                                ON company.id = t.company_id
                              JOIN res_country country
                                ON country.id = company.account_fiscal_country_id
                              JOIN account_fiscal_position afp
                                ON afp.id = t.fiscal_position_id
                             WHERE {{parallel_filter}}
                               AND country.code = 'BR'
                               AND afp.l10n_br_is_avatax
                        )
                        UPDATE {table} t
                           SET l10n_br_goods_operation_type_id =
                                   CASE
                                       WHEN %(table)s = 'account_move' AND t.{am_field1} IS NOT NULL THEN %(type3)s
                                       -- HACK: varchar conversion is only needed to prevent errors in PGSQL
                                       --       due to an irrelevant type mismatch between t.id and 'out_refund'
                                       WHEN %(table)s = 'account_move' AND t.{am_field2}::varchar = 'out_refund' THEN %(type60)s
                                       ELSE %(type1)s
                                   END
                          FROM _is_avatax
                         WHERE _is_avatax.id = t.id
                        """,
                        table=table,
                        # HACK: avoid SQL error for tables other than `account_move` (which overrides the compute method)
                        am_field1="debit_origin_id" if table == "account_move" else "id",
                        am_field2="move_type" if table == "account_move" else "id",
                    ),
                    {
                        "table": table,
                        "type1": op_type1_id,
                        "type3": op_type3_id,
                        "type60": op_type60_id,
                    },
                ).decode(),
                table=table,
                alias="t",
            )
