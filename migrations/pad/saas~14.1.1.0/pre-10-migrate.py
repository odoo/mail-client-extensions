# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT pad_server, pad_key FROM res_company WHERE pad_server IS NOT NULL")
    if cr.rowcount:
        if cr.rowcount > 1:
            raise util.MigrationError(
                "Upgrade of multiple pad servers and keys is not supported. "
                "Please set the same pad configuration on all your companies."
            )
        pad_server, pad_key = cr.fetchone()
        ICP = util.env(cr)["ir.config_parameter"]
        ICP.set_param("pad.pad_server", pad_server)
        ICP.set_param("pad.pad_key", pad_key)

    util.remove_field(cr, "res.company", "pad_server")
    util.remove_field(cr, "res.company", "pad_key")
