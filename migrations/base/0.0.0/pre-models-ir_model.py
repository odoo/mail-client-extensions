# -*- coding: utf-8 -*-
from odoo import models
from odoo.addons.base.maintenance.migrations import util

try:
    from odoo.addons.base.models import ir_model as _ignore  # noqa
except ImportError:
    # version 10
    from odoo.addons.base.ir import ir_model as _ignore  # noqa


def migrate(cr, version):
    pass


class Model(models.Model):
    _inherit = "ir.model"
    _module = "base"

    def unlink(self):
        models = self.mapped("model")
        raise util.MigrationError(
            "💥 It's look like you forgot to call `util.remove_model` on the following models: %s" % ", ".join(models)
        )
        return super(Model, self).unlink()


class Field(models.Model):
    _inherit = "ir.model.fields"
    _module = "base"

    def unlink(self):
        unlink_fields = self.env["ir.model.fields"]
        for field in self:
            if field.model in self.env:
                model = self.env[field.model]
                f = model._fields.get(field.name)
                if f and f.inherited:
                    # See https://github.com/odoo/odoo/pull/53632
                    util._logger.critical(
                        "The field %s.%s is deleted but is still in the registry. It may come from a delegated field.",
                        field.model,
                        field.name,
                    )
                    continue
                elif any("mixin" in m and f.name in self.env[m]._fields for m in model._inherit):
                    # See https://github.com/odoo/odoo/issues/49354
                    util._logger.critical(
                        "The field %s.%s is deleted but is still in the registry. It comes from a mixin model.",
                        field.model,
                        field.name,
                    )
                    continue
            unlink_fields |= field
        if unlink_fields:
            fields = ["%s.%s" % (f.model, f.name) for f in unlink_fields]
            raise util.MigrationError(
                "💥 It's look like you forgot to call `util.remove_field` on the following fields: %s"
                % ", ".join(fields)
            )
        return super(Field, unlink_fields).unlink()
