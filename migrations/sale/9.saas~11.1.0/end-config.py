# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    conf = {}
    if util.ENVIRON.get("sale_layout_installed"):
        conf["group_sale_layout"] = 1

    if util.ENVIRON.get("warning_installed"):
        conf["group_warning_sale"] = 1

    if conf:
        util.env(cr)["sale.config.settings"].create(conf).execute()
