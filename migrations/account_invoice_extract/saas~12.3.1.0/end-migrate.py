# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if "extract_show_ocr_option_selection" in util.ENVIRON:
        cr.executemany(
            "UPDATE res_company SET extract_show_ocr_option_selection = %s WHERE id = %s",
            util.ENVIRON["extract_show_ocr_option_selection"],
        )
