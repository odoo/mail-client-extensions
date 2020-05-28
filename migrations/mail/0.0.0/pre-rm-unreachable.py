# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # NOTE: `mail_alias` table is a special case for mutliple reasons:
    #   - As there is 2 res_model/res_id combinations, they cannot be run in
    #     parallel in one pass,otherwise we got concurrent access errors.
    #   - A null `res_id` is ok. Records should not be removed in this case.

    # start by fixing the one2one of mail.alias.mixin records
    alias_queries = []
    cr.execute(
        """
            SELECT m.id, m.model
              FROM mail_alias a
              JOIN ir_model m ON m.id = a.alias_parent_model_id
             WHERE COALESCE(a.alias_parent_thread_id, 0) != 0
          GROUP BY m.id, m.model
        """
    )
    for mid, model in cr.fetchall():
        table = util.table_of_model(cr, model)
        if not util.column_exists(cr, table, "alias_id"):
            # XXX delete all aliases?
            continue

        alias_queries.append(
            cr.mogrify(
                """
                    UPDATE mail_alias a
                       SET alias_parent_thread_id = t.id
                      FROM {table} t
                     WHERE t.alias_id = a.id
                       AND a.alias_parent_model_id = %s
                       AND a.alias_parent_thread_id != t.id
                """.format(
                    table=table
                ),
                [mid],
            )
        )
    util.parallel_execute(cr, alias_queries)

    mail_queries = []
    for ir in util.indirect_references(cr, bound_only=True):
        if ir.table == "mail_alias":
            util.parallel_execute(
                cr,
                [
                    "{query} AND {ir.res_id} IS NOT NULL AND {ir.res_id} != 0".format(query=query, ir=ir)
                    for query in util.generate_indirect_reference_cleaning_queries(cr, ir)
                ],
            )
        elif ir.table in ["mail_mail_statistics", "mailing_trace"]:
            # statistics table (renamed in saas~12.5) has a NULLABLE m2o to `mail_mail`.
            # Removing a `mail_message` will also remove the linked `mail_mail`, forcing NULL on `mail_mail_statistics`
            # We should then proccess them separately.
            util.parallel_execute(cr, list(util.generate_indirect_reference_cleaning_queries(cr, ir)))
        elif ir.table.startswith("mail_"):
            mail_queries.extend(util.generate_indirect_reference_cleaning_queries(cr, ir))

    util.parallel_execute(cr, mail_queries)
