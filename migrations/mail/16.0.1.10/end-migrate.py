import os
from collections import defaultdict

import lxml

from odoo.modules import get_manifest, get_modules
from odoo.tools.misc import file_open

from odoo.upgrade import util


def update_template_fs(cr, model):
    cr.execute(
        """
        SELECT res_id,
               name,
               module
          FROM ir_model_data
         WHERE model = %s
           AND name IS NOT NULL
           AND module IN %s
        """,
        (
            model,
            tuple(get_modules()),
        ),
    )
    record_info = defaultdict(list)
    for data in cr.dictfetchall():
        record_info[data["module"]].append([data["res_id"], data["name"]])

    for module, vals in record_info.items():
        manifest = get_manifest(module)
        files = filter(lambda file: file.endswith(".xml"), manifest.get("data", []))
        # Try to look in those files first which have more chances of having data records
        files = sorted(files, key=lambda file: not file.endswith("_data.xml"))
        processed_templates = set()
        # We try to lessen the file operations, so we search all the templates for opened file,
        # rather than searching in multiple files for a single templale
        for file in files:
            with file_open(os.path.join(module, file)) as fp:
                doc = lxml.etree.parse(fp)
            for template_id, xml_id in vals:
                # Skip the process if a template is already found previously (in another file)
                if xml_id in processed_templates:
                    continue
                if doc.xpath(f"//record[@id='{xml_id}' or @id='{module}.{xml_id}']"):
                    cr.execute(
                        util.format_query(
                            cr, "UPDATE {} SET template_fs = %s WHERE id = %s", util.table_of_model(cr, model)
                        ),
                        [os.path.join(module, file), template_id],
                    )
                    processed_templates.add(xml_id)
            # If all the external ids are processed, no need to check remaining files
            if len(processed_templates) == len(vals):
                break


def migrate(cr, version):
    update_template_fs(cr, "mail.template")
