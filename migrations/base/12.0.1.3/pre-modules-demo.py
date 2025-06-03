from mock import patch

from odoo.modules import loading
from odoo.tools import xml_import

from odoo.addons.base.maintenance.migrations import util


class new_xml_import(xml_import):
    def _tag_function(self, rec, data_node=None, mode=None):
        if (
            any(map(self.xml_filename.endswith, util.ENVIRON["_upg_force_update_xmlids"]))
            and rec.get("name") == "_update_xmlids"
            and rec.get("model") == "ir.model.data"
            and self.noupdate
            and data_node is not None
            and data_node.get("noupdate") == "1"
        ):
            data_node.set("noupdate", value="0")
            self.noupdate = False

            super()._tag_function(rec, data_node, mode)

            self.noupdate = True
            data_node.set("noupdate", value="1")
            return

        super()._tag_function(rec, data_node, mode)


orig_load_data = loading.load_data


def new_load_data(*args, **kwargs):
    if not util.ENVIRON.get("_upg_force_update_xmlids", None):
        return orig_load_data(*args, **kwargs)
    with patch("odoo.tools.convert.xml_import", new_xml_import):
        return orig_load_data(*args, **kwargs)


loading.load_data = new_load_data


def migrate(cr, version):
    cr.execute("SELECT 1 FROM ir_module_module WHERE name = 'base' AND demo")
    if not cr.rowcount:
        return
    util.ENVIRON["_upg_force_update_xmlids"] = [
        filename
        for filename in [
            "product/data/product_demo.xml",
            "sale/data/sale_demo.xml",
            "website_sale/data/demo.xml",
        ]
        if util.module_installed(cr, filename.split("/")[0])
    ]
