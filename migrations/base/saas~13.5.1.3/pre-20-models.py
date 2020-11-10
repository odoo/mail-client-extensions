# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_model(cr, "base.document.layout", "base", "web")
    util.create_column(cr, "report_layout", "sequence", "integer")
    cr.execute("UPDATE report_layout SET sequence = id")

    util.remove_field(cr, "res.country", "image")
    util.create_column(cr, "res_country", "zip_required", "boolean", default=True)
    util.create_column(cr, "res_country", "state_required", "boolean", default=False)

    cr.execute("UPDATE res_country SET zip_required = false WHERE code IN ('ao', 'bj', 'bz', 'hk', 'ie', 'mo')")
    cr.execute(
        "UPDATE res_country SET state_required = true WHERE code IN ('ar', 'au', 'ca', 'id', 'in', 'it', 'jp', 'mx', 'us')"
    )

    # Cleanup unreachable records
    cr.execute("DELETE FROM res_currency_rate WHERE currency_id IS NULL")
