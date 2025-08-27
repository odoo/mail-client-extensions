from odoo.upgrade import util


def migrate(cr, version):
    if util.version_gte("saas~18.5"):
        # tag_negate is removed
        return
    cr.execute(
        """
        ALTER TABLE account_account_tag
        DROP CONSTRAINT account_account_tag_name_uniq;
        """
    )

    cr.execute(
        """
        UPDATE account_account_tag tag
            SET name = jsonb_build_object(
                       'en_US',
                        CASE WHEN tag.name->>'en_US' LIKE '+%' THEN '-' ELSE '+' END
                        || SUBSTRING(tag.name->>'en_US', 2)
                        ),
                tax_negate = NOT COALESCE(tag.tax_negate, FALSE)
           FROM res_country country
          WHERE tag.country_id = country.id
            AND country.code = 'DE'
            AND tag.name->>'en_US' ~ '[+-](59|61|62|63|64|66|67)$'
        """
    )

    cr.execute(
        """
        ALTER TABLE account_account_tag
                ADD CONSTRAINT account_account_tag_name_uniq
                        UNIQUE (name, applicability, country_id)
        """
    )
