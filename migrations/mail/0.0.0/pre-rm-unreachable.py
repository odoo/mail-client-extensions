# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # NOTE: `mail_alias` table is a special case for mutliple reasons:
    #   - As there is 2 res_model/res_id combinations, they cannot be run in
    #     parallel in one pass,otherwise we got concurrent access errors.
    #   - A null `res_id` is ok. Records should not be removed in this case.
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
        elif ir.table.startswith("mail_"):
            mail_queries.extend(util.generate_indirect_reference_cleaning_queries(cr, ir))

    util.parallel_execute(cr, mail_queries)
