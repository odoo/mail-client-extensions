# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "base.main_company_scss")

    util.force_noupdate(cr, "web.report_assets_common", False)
    util.force_noupdate(cr, "web.external_layout", False)
    util.force_noupdate(cr, "web.internal_layout", False)

    for layout in {"background", "boxed", "clean", "standard"}:
        util.force_noupdate(cr, f"web.external_layout_{layout}", False)
