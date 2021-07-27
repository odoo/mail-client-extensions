# -*- coding: utf-8 -*-
import os

from odoo import tools

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    full_path = env["ir.attachment"]._full_path

    cr.execute(
        """
        SELECT t.id, a.store_fname
          FROM sign_template as t
          JOIN ir_attachment as a ON t.attachment_id = a.id
        """
    )

    has_ids = []
    no_ids = []
    for template_id, store_fname in cr.fetchall():
        if store_fname and os.path.isfile(full_path(store_fname)):
            # file exists in disk yay, just recompute fields
            has_ids.append(template_id)
        else:
            # bad news, file is not there. let a cron handle it
            no_ids.append(template_id)
    if has_ids:
        util.recompute_fields(cr, "sign.template", ["num_pages"], ids=has_ids)
    if no_ids:
        # inject the cron which will process the PDFs that weren't available in disk
        if not util.ref(cr, "__upgrade__.post_upgrade_process_sign_pdfs"):
            cron_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "process-pdf-page-number-cron.xml")
            with open(cron_file, "rb") as cron_file_wrapper:
                tools.convert_xml_import(cr, "__upgrade__", cron_file_wrapper, {})
