# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.ENVIRON.get("austria_chart_template_company_ids"):
        cr.execute(
            """
                UPDATE res_company
                   SET chart_template_id = %s
                 WHERE id IN %s
            """,
            [util.ref(cr, "l10n_at.l10n_at_chart_template"), tuple(util.ENVIRON["austria_chart_template_company_ids"])],
        )
