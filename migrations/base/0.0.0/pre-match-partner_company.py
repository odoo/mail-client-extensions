from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    query = """
        UPDATE res_partner p
           SET company_id = NULL
          FROM res_company c
         WHERE p.id = c.partner_id
           AND p.company_id != c.id
           AND p.company_id IS NOT NULL
    """
    util.explode_execute(cr, query, table="res_partner", alias="p")

    query = """
        UPDATE res_partner p
           SET company_id = cp.company_id
          FROM res_partner cp
          JOIN res_company c
            ON cp.company_id = c.id
         WHERE cp.id = p.commercial_partner_id
           AND p.id != cp.commercial_partner_id
           AND p.company_id IS DISTINCT FROM cp.company_id
     RETURNING p.id, p.name, c.id, c.name
    """
    cr.execute(query)

    total = cr.rowcount
    rows = cr.fetchmany(20)
    if rows:
        util.add_to_migration_reports(
            category="Partners",
            format="html",
            message="""
            <details>
                <summary>
                    A total of {} partners were assigned to different companies than their
                    commercial partner. To avoid issues during the upgrade the following
                    parters were updated to match the company of their commercial partner.
                    (Showing only the first {})
                </summary>
                <ul>{}</ul>
            </details>
            """.format(
                total,
                len(rows),
                "\n".join(
                    "<li> Partner {} now belongs to company {}</li>".format(
                        util.get_anchor_link_to_record("res.partner", p_id, p_name),
                        util.get_anchor_link_to_record("res.partner", c_id, c_name),
                    )
                    for p_id, p_name, c_id, c_name in rows
                ),
            ),
        )
