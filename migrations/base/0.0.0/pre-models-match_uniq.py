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

    if util.version_gte("12.0"):

        @api.model_create_multi
        @util.no_selection_cache_validation
        def create(self, vals_list):
            if not getattr(self, "_match_uniq", False) or self.pool.ready:
                return super().create(vals_list)

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
            constraint_fields_list = self.env.cr.fetchall()

            vals_list = list(vals_list)
            # collect the existing and created record ids in a list, that should
            # have the same order as the corresponding vals_list
            record_ids = [False] * len(vals_list)

            # indexes of vals in vals_list for which create() must be called
            create_idx_list = []

            def convert_to_column(f):
                if util.version_gte("saas~17.5"):
                    return f.convert_to_column_insert
                return f.convert_to_column

            # fill in record_ids with existing records
            for idx, vals in enumerate(vals_list):
                for [constraint_fields] in constraint_fields_list:
                    missing = [f for f in constraint_fields if f not in vals]
                    if missing:
                        vals.update(self.default_get(missing))
                    if any(f not in vals for f in constraint_fields):
                        continue
                    domain = [(f, "=", vals[f]) for f in constraint_fields]
                    record = self.with_context(active_test=False).search(domain, limit=1)
                    if not record:
                        continue
                    xmlid = record.get_metadata()[0]["xmlid"]
                    if xmlid and not xmlid.startswith("__export__."):
                        # XXX raise?
                        _logger.warning(
                            "Matching record %r using domain %r has XMLID %r. Missing rename?", record, domain, xmlid
                        )
                    store_values = {
                        key: convert_to_column(record._fields[key])(value, record)
                        for key, value in vals.items()
                        if record._fields[key].column_type
                    }
                    other_values = {key: value for key, value in vals.items() if key not in store_values}
                    record._write(store_values)
                    record.write(other_values)

                    match_warning = getattr(self, "_match_uniq_warning", False)
                    if match_warning:
                        _logger.log(
                            util.NEARLYWARN if util.on_CI() else logging.WARNING,
                            match_warning.format(xmlid=xmlid, **vals),
                        )
                        util.add_to_migration_reports(
                            message=match_warning.format(xmlid=xmlid, **vals), category="Merged Records"
                        )
                    record_ids[idx] = record.id
                    break
                else:
                    # no record was found above, we have to create this one
                    create_idx_list.append(idx)

            # create the records that must be created, and put their id in record_ids
            if create_idx_list:
                records = super().create([vals_list[idx] for idx in create_idx_list])
                for idx, id_ in zip(create_idx_list, records._ids):
                    record_ids[idx] = id_

            # return result as a recordset
            return self.browse(record_ids)

    else:

        @api.model
        @util.no_selection_cache_validation
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
                    store_values = {
                        key: record._fields[key].convert_to_column(value, record)
                        for key, value in values.items()
                        if record._fields[key].column_type
                    }
                    other_values = {key: value for key, value in values.items() if key not in store_values}
                    record._write(store_values)
                    record.write(other_values)

                    match_warning = getattr(self, "_match_uniq_warning", False)
                    if match_warning:
                        _logger.log(
                            util.NEARLYWARN if util.on_CI() else logging.WARNING,
                            match_warning.format(xmlid=xmlid, **values),
                        )
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
        _name = model
        _inherit = [model]
        _module = "base"
        _match_uniq = True
