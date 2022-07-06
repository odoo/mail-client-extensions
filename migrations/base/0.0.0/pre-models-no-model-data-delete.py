# -*- coding: utf-8 -*-
import logging
import os

from odoo import api, models

from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.base." + __name__)


def migrate(cr, version):
    util.ENVIRON["__no_model_data_delete"].update(
        {
            "res.country": "unused",
            "res.country.state": "unused",
            "res.lang": "always",
            "res.currency": "unused",
            "res.partner": "always",
            "res.users": "always",
            "ir.module.module": "always",
        }
    )


class IrModelData(models.Model):
    _inherit = "ir.model.data"
    _module = "base"

    @api.model
    def _process_end(self, modules):
        no_model_data_delete = util.ENVIRON.get("__no_model_data_delete")
        if not no_model_data_delete:
            return super(IrModelData, self)._process_end(modules)

        if hasattr(self.pool, "loaded_xmlids"):
            loaded_xmlids = self.pool.loaded_xmlids
        else:
            loaded_xmlids = set(".".join([module, name]) for module, name in self.loads)

        self.env.cr.execute(
            """
                  SELECT model, array_agg(module || '.' || name)
                    FROM ir_model_data
                   WHERE module IN %s
                     AND model IN %s
                     AND res_id IS NOT NULL
                     AND COALESCE(noupdate, false) != true
                GROUP BY model
            """,
            [tuple(modules), tuple(no_model_data_delete.keys())],
        )
        for model, xmlids in self.env.cr.fetchall():
            unloaded_xmlids = set(xmlids) - loaded_xmlids
            if unloaded_xmlids:
                # Do not consider unloaded model data having loaded children model data
                # e.g. `res.partner` model data loaded indirectly through `res.users` model data.
                for inheriting in (self.env[m] for m in self.env[model]._inherits_children):
                    # ignore mixins
                    if inheriting._abstract:
                        continue

                    parent_field = inheriting._inherits[model]
                    for xmlid in list(unloaded_xmlids):
                        record = self.env.ref(xmlid, raise_if_not_found=True)
                        if not record:
                            continue
                        children = inheriting.with_context(active_test=False).search([(parent_field, "=", record.id)])
                        children_xids = {xid for xids in children._get_external_ids().values() for xid in xids}
                        if children_xids & loaded_xmlids:
                            # at least one child was loaded
                            unloaded_xmlids.remove(xmlid)

            if unloaded_xmlids:
                noupdate_forced = False
                if no_model_data_delete.get(model) == "unused":
                    deleted = util.delete_unused(self.env.cr, *unloaded_xmlids)
                    if not all(xmlid in deleted for xmlid in unloaded_xmlids):
                        noupdate_forced = True
                else:
                    for xmlid in unloaded_xmlids:
                        util.force_noupdate(self.env.cr, xmlid)
                    noupdate_forced = True

                if not noupdate_forced:
                    continue

                suppress = set(
                    xmlid
                    for (type_, _, xmlid) in (
                        elem.partition(":") for elem in os.environ.get("suppress_upgrade_warnings", "").split(",")
                    )
                    if type_ == "xmlid"
                )
                ignored_xmlids = unloaded_xmlids & suppress
                if ignored_xmlids:
                    _logger.log(util.NEARLYWARN, "Explictly ignoring unlink of record(s) %s", ",".join(ignored_xmlids))
                error_xmlids = unloaded_xmlids - suppress
                if error_xmlids:
                    error_msg = "It looks like you forgot to call `util.delete_unused` on %s" % (",".join(error_xmlids))
                    _logger.critical(error_msg)

        return super(IrModelData, self)._process_end(modules)
