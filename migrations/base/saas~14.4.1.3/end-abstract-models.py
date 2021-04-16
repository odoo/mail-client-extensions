# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)

    # remove magic and inherited fields from abstract models
    def remove(modelname, fieldname):
        if fieldname != "id":
            util.remove_field(cr, modelname, fieldname, drop_column=False, skip_inherit="*")
            return

        # special case for field "id": we cannot use util.remove_field() because it
        # would remove the model; instead we do it the manual way
        cr.execute(
            "DELETE FROM ir_model_fields WHERE model=%s AND name=%s RETURNING id",
            [modelname, "id"])
        fids = tuple(row[0] for row in cr.fetchall())
        if fids:
            cr.execute(
                "DELETE FROM ir_model_data WHERE model=%s AND res_id IN %s",
                ["ir.model.fields", fids])

    for model in env.values():
        if model._abstract:
            # collect magic and inherited fields
            fnames = {"id", "display_name", model.CONCURRENCY_CHECK_FIELD}
            for parent_name in model._inherits:
                for fname in env[parent_name]._fields:
                    if fname not in model._fields:
                        fnames.add(fname)
            # remove them
            for fname in fnames:
                if fname not in model._fields:
                    remove(model._name, fname)
