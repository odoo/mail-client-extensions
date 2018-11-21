# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "website_sale_dashboard_onboarding_state", "varchar")
    cr.execute(
        """
        UPDATE res_company
           SET website_sale_dashboard_onboarding_state =
                  CASE WHEN base_onboarding_company_state IN ('just_done', 'done')
                        AND payment_acquirer_onboarding_state IN ('just_done', 'done')
                        AND account_onboarding_sale_tax_state IN ('just_done', 'done')
                       THEN 'just_done'
                       ELSE 'not_done'
                   END
    """
    )

    util.remove_view(cr, "website_sale_dashboard.sale_dashboard_search_view")
