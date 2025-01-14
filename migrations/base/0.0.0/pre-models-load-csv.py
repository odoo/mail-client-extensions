# -*- coding: utf-8 -*-
from odoo import models
from odoo.models import fix_import_export_id_paths

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pass


class Base(models.AbstractModel):
    _inherit = "base"
    _module = "base"

    def load(self, fields, data):
        # Avoid the overhead from the import feature we don't need to load module's CSV files
        # Specifically, avoid the savepoints `model_load` and `model_load_save` which are useless
        # for the load of module's CSV file, and cause performance issue
        # because more than 64 savepoints can be created during the same transaction.
        # There is no reason data from CSV file are not treated as data from XML files
        # Since saas~18.3, a constant number of savepoints is used during loading.
        if not self.env.context.get("install_module") or util.version_gte("saas~18.3"):
            return super(Base, self).load(fields, data)

        current_module = self.env.context.get("module", "__import__")
        mode = self.env.context.get("mode", "init")
        noupdate = self.env.context.get("noupdate", False)

        fields = [fix_import_export_id_paths(f) for f in fields]
        # In case the xmlid for a many2one doesn't include its module in the xmlid
        data = [
            [
                "{}.{}".format(current_module, value)
                if value and len(field) == 2 and field[1] == "id" and "." not in value
                else value
                for field, value in zip(fields, d)
            ]
            for d in data
        ]
        extracted = self._extract_records(fields, data)
        converted = self._convert_records(extracted)
        ids = []
        if hasattr(self, "_load_records"):
            data_list = [
                {
                    "xml_id": xid if "." in xid else "{}.{}".format(current_module, xid),
                    "values": vals,
                    "info": info,
                    "noupdate": noupdate,
                }
                for _id, xid, vals, info in converted
            ]
            records = self._load_records(data_list, mode == "update")
            ids.extend(records.ids)
        else:
            for _id, xid, vals, _info in converted:
                ids.append(
                    self.env["ir.model.data"]._update(
                        self._name, current_module, vals, mode=mode, xml_id=xid, noupdate=noupdate, res_id=_id
                    )
                )
        return {
            "ids": ids,
            "messages": [],
            "nextrow": 0,
        }
