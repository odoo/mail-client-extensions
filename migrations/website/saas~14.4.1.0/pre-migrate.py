# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # TODO: remove later when renaming is backported
    if util.column_exists(cr, "theme_ir_asset", "glob"):
        util.rename_field(cr, "theme.ir.asset", "glob", "path")

    util.create_column(cr, "website", "sequence", "int4")
    cr.execute("UPDATE website SET sequence = id")
    # 'localhost' is the old website default value (XML). Now, ICP calls are
    # replaced by `get_base_url()` that will prefer website domain over ICP, we
    # don't want links to be send with localhost, see commit msg.
    cr.execute("UPDATE website SET domain = NULL WHERE domain = 'localhost'")
    util.create_column(cr, "res_company", "website_id", "int4")
