# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("saas~17.5"):
        # FIXME
        return  # nosemgrep: no-early-return
        # upgrading to version >= saas-17.5 with jsonb company dependent
        # in the following SQL
        # we will clean
        # 1. column "res_partner"."specific_property_product_pricelist"
        #        column data is like {"company_id": pricelist_id"}
        #        if the pricelist_id referred record's product_pricelist.company_id is not equal to the company_id
        #            remove the key value pair
        # 2. row for "ir_config_parameter" with "key" LIKE 'res.partner.property_product_pricelist%'
        #        if the "key" = 'res.partner.property_product_pricelist' and "value" can be converted to integer
        #            the referred product.pricelist might be the property_product_pricelist for any res.partner
        #            when read with_context with an company. So the product_pricelist.company_id must be NULL
        #        if the "key" like 'res.partner.property_product_pricelist_%s' and "value" can be converted to integer
        #            the referred product.pricelist might be the property_product_pricelist for any res.partner
        #            when read with_context of the % matched company_id. So the product_pricelist.company_id must be
        #            equal to the matched company_id
        # and return the result
        # 1. if partner_id IS NOT NULL AND property_company IS NOT NULL
        #    the row is for a removed specified value in "res_partner"."specific_property_product_pricelist"
        # 2. if partner_id IS NOT NULL AND property_company IS NULL
        #    the row is for a deleted ir_config_parameter whose "key" like 'res.partner.property_product_pricelist_%'
        # 3. if partner_id IS NULL AND property_company IS NULL
        #    the row is for a deleted ir_config_parameter whose "key" = 'res.partner.property_product_pricelist'
        cr.execute(
            r"""
            CREATE TEMPORARY TABLE __upgrade_partner_to_delete AS
            WITH partner_specific_pricelist AS (
                SELECT p.id,
                       p.name,
                       d.k::int4 AS company_id,
                       d.v::int4 AS pricelist_id
                  FROM res_partner p,
                       jsonb_each_text(p.specific_property_product_pricelist) AS d(k, v)
                 WHERE p.specific_property_product_pricelist IS NOT NULL
                   AND d.v ~ '\d+'
            )
            SELECT psp.id AS partner_id,
                   psp.name AS partner_name,
                   psp.company_id AS psp_company_id,
                   psp.pricelist_id AS psp_pricelist_id,
                   pp.id AS pp_id,
                   pp.name AS pp_name,
                   pp.company_id AS pp_company_id
              FROM partner_specific_pricelist psp
              JOIN product_pricelist pp
                ON pp.id = psp.pricelist_id
               AND pp.company_id IS NOT NULL
               AND pp.company_id != psp.company_id
            """
        )
        cr.execute(
            """
            WITH partner_agg_to_delete AS (
                SELECT partner_id, array_agg(psp_company_id)::text[] AS to_delete_company_ids
                  FROM __upgrade_partner_to_delete
              GROUP BY partner_id
            )
           UPDATE res_partner
              SET specific_property_product_pricelist = NULLIF(
                      specific_property_product_pricelist - d.to_delete_company_ids,
                      '{}'::jsonb
                  )
             FROM partner_agg_to_delete d
            WHERE res_partner.id = d.partner_id
            """
        )
        cr.execute(
            r"""
            WITH config_delete AS (
                DELETE FROM ir_config_parameter
                 USING product_pricelist pp
                 WHERE (   key = 'res.partner.property_product_pricelist'
                       AND (CASE WHEN value ~ '^\d+$' THEN value::integer END) = pp.id
                       AND pp.company_id IS NOT NULL)
                   OR (    key ~ '^res\.partner\.property_product_pricelist_\d+$'
                       AND (CASE WHEN value ~ '^\d+$' THEN value::integer END) = pp.id
                      AND replace(key, 'res.partner.property_product_pricelist_', '')::integer != pp.company_id)
            RETURNING value::integer AS psp_company_id,
                      pp.id AS pp_id,
                      pp.company_id AS pp_company_id,
                      pp.name AS pp_name
            )
                SELECT psp_company.name as property_company, pp_company.name as pricelist_company,
                       pd.partner_name as partner_name, pd.partner_id as partner_id,
                       pd.pp_name as pricelist_name, pd.pp_id as pricelist_id
                  FROM __upgrade_partner_to_delete pd
                  JOIN res_company pp_company ON pp_company.id = pd.pp_company_id
                  JOIN res_company psp_company ON psp_company.id = pd.psp_company_id
                 UNION
                SELECT psp_company.name as property_company, pp_company.name as pricelist_company,
                       NULL as partner_name, NULL as partner_id,
                       cd.pp_name AS pricelist_name, cd.pp_id AS pricelist_id
                  FROM config_delete cd
             LEFT JOIN res_company pp_company ON pp_company.id = cd.pp_company_id
             LEFT JOIN res_company psp_company ON psp_company.id = cd.psp_company_id
            """
        )
    else:
        cr.execute(
            """
            WITH deleted AS (
                   DELETE FROM ir_property property
                    USING ir_model_fields field,
                          product_pricelist pricelist
                    WHERE field.model = 'res.partner' and field.name = 'property_product_pricelist'
                      AND property.name = 'property_product_pricelist'
                      AND pricelist.id = replace(value_reference, 'product.pricelist,', '')::integer
                      AND pricelist.company_id IS NOT NULL
                      AND (pricelist.company_id != property.company_id OR property.company_id IS NULL)
                RETURNING property.res_id as res_id,
                          pricelist.id as pricelist_id,
                          property.company_id as property_company_id
            )
               SELECT property_company.name as property_company, pricelist_company.name as pricelist_company,
                      partner.name as partner_name, partner.id as partner_id,
                      pricelist.name as pricelist_name, pricelist.id as pricelist_id
                 FROM deleted
                 JOIN product_pricelist pricelist ON pricelist.id = deleted.pricelist_id
                 JOIN res_company pricelist_company ON pricelist_company.id = pricelist.company_id
            LEFT JOIN res_company property_company ON property_company.id = deleted.property_company_id
            LEFT JOIN res_partner partner ON partner.id = replace(res_id, 'res.partner,', '')::integer
            """
        )
    deleted = cr.dictfetchall()
    if deleted:
        util.add_to_migration_reports(
            """
                <details>
                <summary>
                    While browsing the database using the company "{}",
                    some partners were assigned pricelists from the company "{}",
                    and the other way around as well.
                    As this is not a valid configuration, the pricelists of these partners have been unassigned.
                    If you want these partners to have an assigned pricelist, you will need to reassign them.
                    You will find the list of the partners updated below.
                </summary>
                <ul>
                    {}
                </ul>
                </details>
            """.format(
                util.html_escape(deleted[0]["property_company"]),
                util.html_escape(deleted[0]["pricelist_company"]),
                "\n".join(
                    """
                        <li>
                            {msg_browsing}
                            {msg_partner}
                            "{pricelist_name}" (#{pricelist_id}) from the company "{pricelist_company}"
                        </li>
                    """.format_map(
                        dict(
                            row,
                            msg_browsing=(
                                'While browsing the company "{}",'.format(util.html_escape(row["property_company"]))
                            )
                            if row["property_company"]
                            else "While browsing any company",
                            msg_partner=(
                                'the partner "{}" (#%{}) used the pricelist'.format(
                                    util.html_escape(row["partner_name"]), row["partner_id"]
                                )
                            )
                            if row["partner_id"]
                            else "the default pricelist was",
                        )
                    )
                    for row in deleted
                ),
            ),
            "Pricelists",
            format="html",
        )
