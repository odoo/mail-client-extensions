# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def _get_model_id(cr, model):
    cr.execute("SELECT id FROM ir_model WHERE model=%s", (model,))
    return cr.fetchone()[0]


def migrate(cr, version):
    cr.execute(
        """
        SELECT name, src_model, dst_model
          FROM mig_s124_accountfieldstotransfer
         WHERE state='manual'
        """
    )
    for field, src_model, dst_model in [(p[0], p[1], p[2]) for p in cr.fetchall()]:
        cr.execute(
            "UPDATE ir_model_fields SET model=%s, model_id=%s WHERE model=%s AND name=%s RETURNING id",
            (dst_model, _get_model_id(cr, dst_model), src_model, field),
        )
