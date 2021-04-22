# -*- coding: utf-8 -*-
import os

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
        invalid_models = []
        for model in self.mapped("model"):
            if "model:%s" % model in os.environ.get("suppress_upgrade_warnings", "").split(","):
                util._logger.log(25, "Model unlink %s explicitly ignored, skipping" % model)
            else:
                invalid_models.append(model)
        if invalid_models:
            raise util.MigrationError(
                "💥 It looks like you forgot to call `util.remove_model` on the following models: %s"
                % ", ".join(invalid_models)
            )
        return super(Model, self).unlink()


class Field(models.Model):
    _inherit = "ir.model.fields"
    _module = "base"

    def unlink(self):
        unlink_fields = self.env["ir.model.fields"]
        ignore_fields = self.env["ir.model.fields"]
        for field in self:
            model = self.env[field.model] if field.model in self.env else None
            f = model._fields.get(field.name) if model else None
            if "field:%s.%s" % (field.model, field.name) in os.environ.get("suppress_upgrade_warnings", "").split(","):
                ignore_fields |= field
                util._logger.log(25, "Field unlink %s.%s explicitly ignored, skipping" % (field.model, field.name))
                continue
            elif f and f.inherited:
                # See https://github.com/odoo/odoo/pull/53632
                util._logger.critical(
                    "The field %s.%s is being deleted but is still in the registry. "
                    "It may come from a delegated field.",
                    field.model,
                    field.name,
                )
                continue
            elif f and any("mixin" in m and f.name in self.env[m]._fields for m in model._inherit):
                # See https://github.com/odoo/odoo/issues/49354
                util._logger.critical(
                    "The field %s.%s is being deleted but is still in the registry. It comes from a mixin model.",
                    field.model,
                    field.name,
                )
                continue
            elif not f and field.related:
                model = field.model
                for name in field.related.split("."):
                    r = self.env["ir.model.fields"].search([("model", "=", model), ("name", "=", name)])
                    if not r:
                        # See https://github.com/odoo/odoo/issues/49354
                        util._logger.critical(
                            """
                                The field %s.%s is deleted during the upgrade.
                                Since this is a related field for which the related doesn't exist,
                                this might be due to the bug of the mixins
                                not marking the fields on their rightful module"
                            """,
                            field.model,
                            field.name,
                        )
                        ignore_fields |= field
                        break
                    model = r.relation
                else:
                    util._logger.critical(
                        "The field %s.%s is being deleted. Either you forgot to call `util.remove_field`, "
                        "either it is a custom field marked as coming from a standard module "
                        "due to odoo/odoo#49354.",
                        field.model,
                        field.name,
                    )
                    continue
            elif not f and (not field.store or field.ttype == "one2many"):
                # As the field is not stored, no data is actually deleted, so no worries to delete the field
                # Let it be deleted, so the ORM creates it back, hopefully marked with the correct module this time.
                util._logger.critical(
                    """
                        The field %s.%s is deleted during the upgrade.
                        This might be due to the bug of the mixins, not marking the fields on their rightful module.
                        Since this is not a stored field,
                        we let it be deleted, it will be created back by the ORM on the first
                        `-u` on the according module if needed, hopefully marked with the correct module this time
                        "
                    """,
                    field.model,
                    field.name,
                )
                ignore_fields |= field
            elif not f and self.env["ir.model"].search([("model", "=", field.model)]).transient:
                # As it's a transient model, no hard-fail, as transient data is temporary anyway.
                util._logger.critical(
                    "The field %s.%s is being deleted. Either you forgot to call `util.remove_field`, "
                    "either it is a custom field coming from a transient model marked as coming from a standard module",
                    field.model,
                    field.name,
                )
                # Let it be deleted, so the ORM creates it back, hopefully marked with the correct module this time.
                ignore_fields |= field

            unlink_fields |= field
        invalid_unlink_fields = unlink_fields - ignore_fields
        if invalid_unlink_fields:
            fields = ["%s.%s" % (f.model, f.name) for f in invalid_unlink_fields]
            raise util.MigrationError(
                "💥 It looks like you forgot to call `util.remove_field` on the following fields: %s" % ", ".join(fields)
            )
        return super(Field, unlink_fields).unlink()
