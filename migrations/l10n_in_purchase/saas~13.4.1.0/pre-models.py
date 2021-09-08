# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # create column in db for new fields in purchase_order table
    util.create_column(cr, "purchase_order", "l10n_in_gst_treatment", "varchar")

    # stored value for field 'l10n_in_gst_treatment' as per partner for existing purchase orders
    cr.execute(
        """
        UPDATE purchase_order p
           SET l10n_in_gst_treatment = rp.l10n_in_gst_treatment
          FROM res_partner rp,
               res_company comp
          JOIN res_partner comp_p ON comp_p.id = comp.partner_id
          JOIN res_country c ON c.id = comp_p.country_id
         WHERE rp.id = p.partner_id
           AND comp.id = p.company_id
           AND c.code = 'IN'
        """
    )
