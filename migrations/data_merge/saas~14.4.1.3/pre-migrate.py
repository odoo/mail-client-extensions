# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "ir_model", "ref_merge_ir_act_server_id", "int4")
    util.create_column(cr, "data_merge_model", "is_contextual_merge_action", "boolean", default=False)
