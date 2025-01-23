from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.util.inconsistencies import break_recursive_loops


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

    break_recursive_loops(cr, "res.partner", "commercial_partner_id")
    query = """
        WITH RECURSIVE info AS (
            SELECT id,
                   company_id
              FROM res_partner
             WHERE (commercial_partner_id IS NULL
                OR commercial_partner_id = id)
               AND {parallel_filter}

             UNION ALL

            SELECT child.id,
                   COALESCE(parent.company_id, child.company_id)
              FROM res_partner child
              JOIN info parent
                ON child.commercial_partner_id = parent.id
               AND child.commercial_partner_id != child.id
        )
        UPDATE res_partner p
           SET company_id = info.company_id
          FROM info
          JOIN res_company comp
            ON info.company_id = comp.id
         WHERE info.id = p.id
           AND info.company_id IS NOT NULL
           AND p.company_id IS DISTINCT FROM info.company_id
     RETURNING p.id, p.name, comp.id, comp.name
    """
    util.explode_execute(cr, query, table="res_partner")

    rows = cr.fetchall()
    if not rows:
        return
    util.add_to_migration_reports(
        category="Partners",
        format="html",
        message="""
        <details>
            <summary>
                Some partners were assigned to different companies than their
                commercial partner. To avoid issues during the upgrade the following
                parters were updated to match the company of their commercial partner.
            </summary>
            <ul>{}</ul>
        </details>
        """.format(
            "\n".join(
                "<li> Partner {} now belongs to company {}</li>".format(
                    util.get_anchor_link_to_record("res.partner", p_id, p_name),
                    util.get_anchor_link_to_record("res.partner", c_id, c_name),
                )
                for p_id, p_name, c_id, c_name in rows
            ),
        ),
    )
