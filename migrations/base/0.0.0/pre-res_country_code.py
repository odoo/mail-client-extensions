from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("17.0", "saas~18.1"):
        cr.execute(
            r"""
            WITH max_integer_code AS (
                SELECT COALESCE(MAX(code::INT), 0) AS max_code
                  FROM res_country
                 WHERE code ~ '^\d+$'
            ),
            numbered_countries AS (
                SELECT id,
                       LPAD((ROW_NUMBER() OVER (ORDER BY id) + (SELECT max_code FROM max_integer_code))::TEXT, 2, '0') AS new_code
                  FROM res_country
                 WHERE code IS NULL
            )
            UPDATE res_country rc
               SET code = nc.new_code
              FROM numbered_countries nc
             WHERE rc.id = nc.id
         RETURNING rc.id, rc.name->>'en_US'
            """
        )
        country_codes = sorted(cr.fetchall())
        if country_codes:
            util.add_to_migration_reports(
                """
                <details>
                    <summary>
                    Some countries had missing code, this is not valid anymore.
                    Those countries got an automatic two-digit code as a placeholder,
                    you can set the correct code yourself.
                    You can find below the list of updated countries.
                    </summary>
                    <ul>{}</ul>
                </details>
                """.format(
                    " ".join(
                        "<li>{}</li>".format(util.get_anchor_link_to_record("res.country", id, name))
                        for id, name in country_codes
                    )
                ),
                category="Country Code",
                format="html",
            )
