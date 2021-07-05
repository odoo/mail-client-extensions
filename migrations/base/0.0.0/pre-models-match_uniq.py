# -*- coding: utf-8 -*-
import logging

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
        if not getattr(self, "_match_uniq", False) or self.pool.ready:
            return super(Base, self).create(values)

        table = util.table_of_model(self.env.cr, self._name)
        self.env.cr.execute(
            """
                  SELECT array_agg(a.attname)
                    FROM pg_index i
                    JOIN pg_attribute a ON a.attrelid = i.indrelid
                                       AND a.attnum = ANY(i.indkey)
                   WHERE i.indrelid = %s::regclass
                     AND i.indisunique
                     AND not i.indisprimary
                GROUP BY i.indexrelid
        """,
            [table],
        )
        for [constraint_fields] in self.env.cr.fetchall():
            if isinstance(values, list):
                assert len(values) == 1
                values = values[0]
            missing = [f for f in constraint_fields if f not in values]
            if missing:
                values.update(self.default_get(missing))
            if any(f not in values for f in constraint_fields):
                continue
            domain = [(f, "=", values[f]) for f in constraint_fields]
            record = self.with_context(active_test=False).search(domain, limit=1)
            if record:
                xmlid = record.get_metadata()[0]["xmlid"]
                if xmlid and not xmlid.startswith("__export__."):
                    # XXX raise?
                    _logger.warning(
                        "Matching record %r using domain %r has XMLID %r. Missing rename?", record, domain, xmlid
                    )
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

        return super(Base, self).create(values)


match_uniq_models = {
    "res.country",
    "res.country.state",
    "res.lang",
    "res.currency",
    "ir.config_parameter",
    "ir.actions.act_window.view",
    "ir.module.module",
}
if util.version_gte("saas~12.5"):
    # decimal.precision is moved into base with odoo/odoo@0c5121a979f02d6eee9779068cbb2d43788dc917
    match_uniq_models.add("decimal.precision")

for model in match_uniq_models:

    class Americaine(models.Model):  # a.k.a "Le grand détournement"
        _inherit = model
        _module = "base"
        _match_uniq = True
