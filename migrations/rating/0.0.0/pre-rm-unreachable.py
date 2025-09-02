# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if "rating" not in util.split_osenv("UPG_CLEAN_UNREACHABLES"):
        return  # nosemgrep: no-early-return

    # NOTE: `rating_rating` table is a special case for mutliple reasons:
    #   - As there is 2 res_model/res_id combinations, they cannot be run in
    #     parallel in one pass,otherwise we got concurrent access errors.
    #   - A null `res_id` is ok. Records should not be removed in this case.
    for ir in util.indirect_references(cr, bound_only=True):
        if ir.table == "rating_rating":
            assert not ir.company_dependent_comodel
            util.parallel_execute(
                cr,
                [
                    "{query} AND {ir.res_id} IS NOT NULL AND {ir.res_id} != 0".format(query=query, ir=ir)
                    for query in util.generate_indirect_reference_cleaning_queries(cr, ir)
                ],
            )
