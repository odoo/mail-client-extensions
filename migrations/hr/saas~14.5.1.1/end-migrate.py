# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Those fields will no longer be used to hold the documents we need,
    # instead we will use the chatter and the documents app.
    # The reason it is done this way is to make sure that the documents app creates
    # the documents for the related files accordingly.
    # See documents/models/ir_attachment.py:write
    # If documents_hr is not installed, just set res_field to NULL on the appropriate records.
    binary_fields_to_process = ("id_card", "driving_license")
    if util.module_installed(cr, "documents_hr"):
        cr.execute(
            """
            SELECT id
              FROM ir_attachment
             WHERE res_model='hr.employee'
               AND res_field in %s
        """,
            (binary_fields_to_process,),
        )
        ids = [id for id, in cr.fetchall()]
        env = util.env(cr)
        util.iter_browse(env["ir.attachment"], ids).write({"res_field": False})
    else:
        cr.execute(
            """
            UPDATE ir_attachment
               SET res_field=NULL
             WHERE res_model='hr.employee'
               AND res_field in %s
        """,
            (binary_fields_to_process,),
        )
