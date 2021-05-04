# -*- coding: utf-8 -*-
import logging

from psycopg2 import IntegrityError

from odoo import api, models

from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger("odoo.addons.base.maintenance.migration.base.000." + __name__)


def migrate(cr, version):
    pass


class Base(models.AbstractModel):
    _inherit = "base"
    _module = "base"

    @api.model
    def create(self, values):
        if not getattr(self, "_match_uniq", False):
            return super(Base, self).create(values)

        try:
            with self.env.cr.savepoint():
                return super(Base, self).create(values)
        except IntegrityError as e:
            if e.pgcode == "23505" and not self.pool.ready:
                self.env.cr.execute(
                    """
                    SELECT a.attname
                      FROM pg_index i
                      JOIN pg_attribute a ON a.attrelid = i.indrelid
                                         AND a.attnum = ANY(i.indkey)
                     WHERE i.indexrelid = %s::regclass
                """,
                    [e.diag.constraint_name],
                )
                constraint_fields = [f for f, in self.env.cr.fetchall()]
                if constraint_fields:
                    if isinstance(values, list):
                        assert len(values) == 1
                        values = values[0]
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
                        store_values = {key: value for key, value in values.items() if record._fields[key].column_type}
                        other_values = {key: value for key, value in values.items() if key not in store_values}
                        record._write(store_values)
                        record.write(other_values)

                        match_warning = getattr(self, "_match_uniq_warning", False)
                        if match_warning:
                            util.add_to_migration_reports(
                                message=match_warning.format(xmlid=xmlid, **values), category="Merged Records"
                            )

                        return record
            raise


for model in {
    "res.country",
    "res.country.state",
    "res.lang",
    "res.currency",
    "ir.config_parameter",
    "ir.actions.act_window.view",
    "ir.module.module",
}:

    class Americaine(models.Model):  # a.k.a "Le grand détournement"
        _inherit = model
        _module = "base"
        _match_uniq = True
