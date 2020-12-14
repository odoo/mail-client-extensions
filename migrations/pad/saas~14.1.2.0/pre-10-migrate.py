# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT (array_agg(name ORDER BY id))[1] company_name, pad_server, pad_key
          FROM res_company
         WHERE pad_server IS NOT NULL
      GROUP BY pad_server, pad_key
      ORDER BY min(id)
      """
    )
    rc = cr.rowcount
    if rc:
        company_name, pad_server, pad_key = cr.fetchone()

        if rc > 1:
            util.add_to_migration_reports(
                "Using different pad configurations across companies is no more supported. "
                f"Only the configuration of {company_name!r} has been kept.",
                "Pad",
            )

        ICP = util.env(cr)["ir.config_parameter"]
        ICP.set_param("pad.pad_server", pad_server)
        ICP.set_param("pad.pad_key", pad_key)

    util.remove_field(cr, "res.company", "pad_server")
    util.remove_field(cr, "res.company", "pad_key")
