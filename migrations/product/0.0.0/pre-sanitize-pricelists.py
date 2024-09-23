# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
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
                        for row in deleted
                    )
                ),
            ),
            "Pricelists",
            format="html",
        )
