# -*- coding: utf-8 -*-
import logging

from odoo import models
from odoo.exceptions import ValidationError

from odoo.addons.uom.models import uom_uom  # noqa

_logger = logging.getLogger("odoo.addons.base.maintenance.migration.uom.000." + __name__)


def migrate(cr, version):
    pass


class UniqError(ValidationError):
    pass


class UoM(models.Model):
    _name = "uom.uom"
    _inherit = ["uom.uom"]
    _module = "uom"
    # _match_uniq = True    # noqa: ERA001 ; Not an SQL unique constraint

    def create(self, values):
        try:
            return super(UoM, self).create(values)
        except UniqError:
            if isinstance(values, list):
                assert len(values) == 1
                values = values[0]
            constraint_fields = ["category_id", "uom_type", "active"]
            default, missing = {}, [f for f in constraint_fields if f not in values]
            if missing:
                default = self.default_get(missing)
            domain = [(f, "=", values.get(f, default.get(f, False))) for f in constraint_fields]
            record = self.with_context(active_test=False).search(domain, limit=1)
            if record:
                xmlid = record.get_metadata()[0]["xmlid"]
                if xmlid and not xmlid.startswith("__export__."):
                    # XXX raise?
                    _logger.warning("Matching record %r has XMLID %r. Missing rename?", record, xmlid)
                record._write(values)
                return record
            raise

    def _check_category_reference_uniqueness(self):
        try:
            super(UoM, self)._check_category_reference_uniqueness()
        except ValidationError as e:
            raise UniqError(e)
