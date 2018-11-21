# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        "UPDATE digest_digest SET kpi_crm_lead_created=true, kpi_crm_opportunities_won=true WHERE id=%s",
        [util.ref(cr, "digest.digest_digest_default")],
    )
