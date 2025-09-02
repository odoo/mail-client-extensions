# -*- coding: utf-8 -*-
import os

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("CREATE TABLE _upgrade_clean_imd(module varchar, name varchar)")

    if not util.str2bool(os.getenv("UPG_SKIP_IMD_CLEANING", "0")):
        wrap_query = """
            WITH del AS (
                {}
                RETURNING module, name
             )
            INSERT INTO _upgrade_clean_imd(module, name)
                 SELECT module, name
                   FROM del
        """.format

        ir = util.IndirectReference("ir_model_data", "model", "res_id")
        util.parallel_execute(
            cr, [wrap_query(query) for query in util.generate_indirect_reference_cleaning_queries(cr, ir)]
        )
