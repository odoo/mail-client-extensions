# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT DISTINCT pad_server, pad_key FROM res_company WHERE pad_server IS NOT NULL")
    if cr.rowcount > 1:
        util.add_to_migration_reports("Only one pad server is supported", "Pad")
    elif cr.rowcount == 1:
        pad_server, pad_key = cr.fetchone()
        ICP = util.env(cr)["ir.config_parameter"]
        ICP.set_param("pad.pad_server", pad_server)
        ICP.set_param("pad.pad_key", pad_key)

    util.remove_field(cr, "res.company", "pad_server")
    util.remove_field(cr, "res.company", "pad_key")
