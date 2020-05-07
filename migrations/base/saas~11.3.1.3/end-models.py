# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
from odoo.exceptions import UserError


def migrate(cr, version):
    env = util.env(cr)
    cr.execute(
        """
            SELECT model, array_agg(id)
              FROM ir_model_fields
             WHERE state = 'manual'
               AND related IS NOT NULL
               AND related_field_id IS NULL
          GROUP BY model
        """
    )
    fields_left = env["ir.model.fields"]
    for model, ids in cr.fetchall():
        fields = env["ir.model.fields"].browse(ids)
        if model in env:
            for field in fields:
                try:
                    field._compute_related_field_id()
                # UserError: Unknown field name '..' in related field
                # KeyError: model of field.relation not in registry models
                except (UserError, KeyError):
                    fields_left |= field
        else:
            fields_left |= fields
    if fields_left:
        fields_desc_list = ", ".join("%s.%s" % (field.model, field.name) for field in fields_left)
        util.add_to_migration_reports(
            "Some custom related fields have not been computed because their model or fields they rely on "
            "are defined in modules which were not available during the upgrade: %s" % fields_desc_list,
            "Custom fields",
        )
