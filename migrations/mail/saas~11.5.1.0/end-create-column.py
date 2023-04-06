# -*- coding: utf-8 -*-
from odoo.modules.module import get_modules

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # create message_main_attachment_id for models inheriting mail.thread
    cr.execute(
        r"""
        SELECT m.model
          FROM ir_model m
     LEFT JOIN ir_model_data d
            ON d.res_id = m.id
           AND d.model = 'ir.model'
         WHERE m.is_mail_thread
           AND (  -- a model from a custom module
                  (   d.id IS NOT NULL
                  AND d.module NOT IN %s
                  )
                  -- a custom model created manually
               OR (   d.id IS NULL
                  AND m.state = 'manual'
                  )
               )
        """,
        [tuple(get_modules())],
    )
    for (model,) in cr.fetchall():
        table = util.table_of_model(cr, model)
        if util.table_exists(cr, table):
            util.create_column(cr, table, "message_main_attachment_id", "int4")
