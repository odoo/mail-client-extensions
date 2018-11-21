# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        "UPDATE digest_digest SET kpi_website_sale_total=true WHERE id=%s",
        [util.ref(cr, "digest.digest_digest_default")],
    )
