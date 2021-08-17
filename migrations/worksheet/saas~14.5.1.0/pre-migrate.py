# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "worksheet_template", "res_model", "varchar")
    cr.execute(
        """
        UPDATE worksheet_template wt
           SET res_model = m.model
          FROM ir_model m
         WHERE m.id = wt.res_model_id
        """
    )
    util.remove_field(cr, "worksheet.template", "res_model_id")
