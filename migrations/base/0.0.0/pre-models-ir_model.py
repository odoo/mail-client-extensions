# -*- coding: utf-8 -*-
# ruff: noqa: SIM112, UP031
import os

from odoo import models

from odoo.addons.base.maintenance.migrations import util

try:
    from odoo.addons.base.models import ir_model as _ignore
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
                util._logger.log(util.NEARLYWARN, "Model unlink %s explicitly ignored, skipping", model)
            else:
                invalid_models.append(model)
        if invalid_models:
            message = "💥 It looks like you forgot to call `util.remove_model` on the following models: %s" % ", ".join(
                invalid_models
            )
            if util.on_CI():
                util._logger.critical(message)
            else:
                raise util.MigrationError(message)

        return super(Model, self).unlink()


class Field(models.Model):
    _inherit = "ir.model.fields"
    _module = "base"

    def unlink(self):
        unlink_fields = self.env["ir.model.fields"]
        ignore_fields = self.env["ir.model.fields"]
        for field in self:
            model = self.env.get(field.model)
            f = model._fields.get(field.name) if model is not None else None
            if "field:%s.%s" % (field.model, field.name) in os.environ.get("suppress_upgrade_warnings", "").split(","):
                ignore_fields |= field
                util._logger.log(
                    util.NEARLYWARN, "Field unlink %s.%s explicitly ignored, skipping", field.model, field.name
                )
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

            elif (model is not None) and model._inherit:
                abstract_models = [model for model in self.env.registry.values() if model._abstract]
                inherited_abstracts = {
                    model._name for model in abstract_models if field.model in model._inherit_children
                }
                while True:
                    find_abstracts = {
                        model._name
                        for model in abstract_models
                        if any(m in model._inherit_children for m in inherited_abstracts)
                    }
                    if find_abstracts <= inherited_abstracts:
                        break
                    inherited_abstracts |= find_abstracts

                abstract_fields = (
                    self.env["ir.model.fields"].search_count(
                        [("model", "in", list(inherited_abstracts)), ("name", "=", field.name)]
                    )
                    if inherited_abstracts
                    else 0
                )
                if abstract_fields:
                    util._logger.critical(
                        "The field %s.%s is being deleted. Either you forgot to call `util.remove_field`, either it is "
                        "a custom field marked as coming from a standard module due to odoo/odoo#49354.",
                        field.model,
                        field.name,
                    )
                    continue

            unlink_fields |= field
        invalid_unlink_fields = unlink_fields - ignore_fields
        if invalid_unlink_fields:
            fields = ["%s.%s" % (f.model, f.name) for f in invalid_unlink_fields]
            message = "💥 It looks like you forgot to call `util.remove_field` on the following fields: %s" % ", ".join(
                fields
            )
            if util.on_CI():
                util._logger.critical(message)
            else:
                raise util.MigrationError(message)

        return super(Field, unlink_fields).unlink()
