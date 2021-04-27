# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # create column in db for new fields in sale_order table
    util.create_column(cr, "sale_order", "l10n_in_gst_treatment", "varchar")
    cr.execute(
        """
        UPDATE sale_order s
           SET l10n_in_gst_treatment = p.l10n_in_gst_treatment
          FROM res_partner p,
               res_company comp
          JOIN res_partner comp_p ON comp_p.id = comp.partner_id
          JOIN res_country c ON c.id = comp_p.country_id
         WHERE p.id = s.partner_id
           AND comp.id = s.company_id
           AND c.code = 'IN'
        """
    )

    # create column in db for new fields in res_partner table
    util.create_column(cr, "res_partner", "l10n_in_shipping_gstin", "varchar")
