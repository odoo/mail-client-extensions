# -*- coding: utf-8 -*-
import os

import lxml

from odoo.tools.misc import file_open

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    updates = {}
    cr.execute("SELECT module, array_agg(name) FROM ir_model_data WHERE model = 'res.groups' GROUP BY module")
    for module, xids in cr.fetchall():
        xpath_ids = " or ".join("@id='{}'".format(i) for i in (xids + ["{}.{}".format(module, x) for x in xids]))
        xpath = "//record[{}]/field[@name='category_id']".format(xpath_ids)

        manifest = util.get_manifest(module)
        for f in manifest.get("data", []):
            if not f.endswith(".xml"):
                continue
            with file_open(os.path.join(module, f)) as fp:
                doc = lxml.etree.parse(fp)
                for node in doc.xpath(xpath):
                    group = node.getparent().attrib["id"]
                    if "." not in group:
                        group = "{}.{}".format(module, group)

                    categ = node.attrib["ref"]
                    if "." not in categ:
                        categ = "{}.{}".format(module, categ)

                    updates[util.ref(cr, group)] = util.ref(cr, categ)

    cr.executemany("UPDATE res_groups SET category_id = %s WHERE id = %s", [(v, k) for k, v in updates.items()])

    env = util.env(cr)
    env["res.groups"]._update_user_groups_view()
    env["ir.actions.actions"].clear_caches()


if __name__ == "__main__":
    env = env  # noqa: F821
    migrate(env.cr, None)
    env.cr.commit()
