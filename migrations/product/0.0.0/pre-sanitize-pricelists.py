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
                    While browsing the database using the company "%s",
                    some partners were assigned pricelists from the company "%s",
                    and the other way around as well.
                    As this is not a valid configuration, the pricelists of these partners have been unassigned.
                    If you want these partners to have an assigned pricelist, you will need to reassign them.
                    You will find the list of the partners updated below.
                </summary>
                <ul>
                    %s
                </ul>
                </details>
            """
            % (
                util.html_escape(deleted[0]["property_company"]),
                util.html_escape(deleted[0]["pricelist_company"]),
                "\n".join(
                    """
                        <li>
                            %(msg_browsing)s
                            %(msg_partner)s
                            "%(pricelist_name)s" (#%(pricelist_id)s) from the company "%(pricelist_company)s"
                        </li>
                    """
                    % dict(
                        row,
                        msg_browsing=('While browsing the company "%(property_company)s",' % row)
                        if row["property_company"]
                        else "While browsing any company",
                        msg_partner=('the partner "%(partner_name)s" (#%(partner_id)s) used the pricelist' % row)
                        if row["partner_id"]
                        else "the default pricelist was",
                    )
                    for row in deleted
                ),
            ),
            "Pricelists",
            format="html",
        )
