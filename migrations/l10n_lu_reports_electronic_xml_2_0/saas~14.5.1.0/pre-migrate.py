# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # ===========================================================
    # Task 2526717 : Agent / Fiduciary for XML exports
    # ===========================================================
    util.remove_view(cr, "l10n_lu_reports_electronic_xml_2_0.view_company_form")
    util.remove_view(cr, "l10n_lu_reports_electronic_xml_2_0.view_l10n_lu_generate_xml")
    util.remove_record(cr, "l10n_lu_reports_electronic_xml_2_0.action_l10n_lu_generate_xml")
    util.remove_field(cr, "l10n_lu.generate.xml", "by_fidu")

    # First, look in res_partner to see if the agent already exists.
    # If so, transfer the l10n_lu_agent_* fields from res_company to res_partner,
    # and link the partner to the company.
    cr.execute(
        """
        WITH existing_partner AS (
            SELECT rc.id rc_id,
                   rp.id rp_id,
                   rc.l10n_lu_agent_ecdf_prefix,
                   rc.l10n_lu_agent_matr_number,
                   rc.l10n_lu_agent_rcs_number,
                   rc.l10n_lu_agent_vat
              FROM res_company rc
              JOIN res_partner rp ON rc.l10n_lu_agent_vat = rp.vat
             WHERE rp.company_id IS NULL
                OR rp.company_id = rc.id
        ),
        update_partner AS (
           UPDATE res_partner rp
              SET l10n_lu_agent_ecdf_prefix = ep.l10n_lu_agent_ecdf_prefix,
                  l10n_lu_agent_matr_number = ep.l10n_lu_agent_matr_number,
                  l10n_lu_agent_rcs_number = ep.l10n_lu_agent_rcs_number
             FROM existing_partner ep
            WHERE rp.id = ep.rp_id
        RETURNING rp.id
        )
        UPDATE res_company rc
           SET account_representative_id = up.id
          FROM update_partner up
          JOIN existing_partner ep ON ep.rp_id = up.id
         WHERE rc.id = ep.rc_id;
        """
    )

    # If the partner does not exist, create it with a generic name.
    cr.execute(
        """
        WITH insert_partner AS (
            INSERT INTO res_partner (
                                     company_id,
                                     name,
                                     l10n_lu_agent_ecdf_prefix,
                                     l10n_lu_agent_matr_number,
                                     l10n_lu_agent_rcs_number,
                                     vat
                )
                SELECT id                        comp_id,
                       'Agent of ' || rc.name    partner_name,
                       l10n_lu_agent_ecdf_prefix partner_ecdf,
                       l10n_lu_agent_matr_number partner_matr,
                       l10n_lu_agent_rcs_number  partner_rcs,
                       l10n_lu_agent_vat         partner_vat
                  FROM res_company rc
                 WHERE (
                         l10n_lu_agent_ecdf_prefix IS NOT NULL
                         OR l10n_lu_agent_matr_number IS NOT NULL
                         OR l10n_lu_agent_rcs_number IS NOT NULL
                         OR l10n_lu_agent_vat IS NOT NULL
                     )
                   AND account_representative_id IS NULL
             RETURNING id, company_id
        )
        UPDATE res_company rc
           SET account_representative_id = ip.id
          FROM insert_partner ip
         WHERE rc.id = ip.company_id;
        """
    )

    util.remove_field(cr, "res.company", "l10n_lu_agent_vat")
    util.remove_field(cr, "res.company", "l10n_lu_agent_matr_number")
    util.remove_field(cr, "res.company", "l10n_lu_agent_ecdf_prefix")
    util.remove_field(cr, "res.company", "l10n_lu_agent_rcs_number")
