# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    stages = {
        q: util.ref(cr, "sale_subscription.sale_subscription_stage_" + q)
        for q in {"draft", "in_progress", "upsell", "closed"}
    }

    cr.execute(
        """
        UPDATE sale_subscription
           SET stage_id = CASE state WHEN 'draft' THEN %(draft)s
                                     WHEN 'open' THEN %(in_progress)s
                                     WHEN 'pending' THEN %(in_progress)s
                                     WHEN 'close' THEN %(closed)s
                                     WHEN 'cancel' THEN %(closed)s
                                     ELSE NULL
                           END
    """,
        stages,
    )

    util.remove_field(cr, "sale.subscription", "state")
