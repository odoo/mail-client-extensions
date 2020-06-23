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
        fields = ["%s.%s" % (f.model, f.name) for f in self]
        raise util.MigrationError(
            "💥 It's look like you forgot to call `util.remove_field` on the following fields: %s" % ", ".join(fields)
        )
        return super(Field, self).unlink()
