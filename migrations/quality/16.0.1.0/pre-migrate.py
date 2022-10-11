# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "quality_check", "note", "text")
    query = """
        UPDATE quality_check qc
           SET note = qp.note
          FROM quality_point qp
         WHERE qc.point_id = qp.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="quality_check", alias="qc"))
