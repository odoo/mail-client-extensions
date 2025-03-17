from odoo.upgrade import util


def migrate(cr, version):
    # odoo/odoo#125642
    # res.company.parent_id is repurposed to identify subsidiaries
    cr.execute(
        """
        UPDATE res_company cc
           SET parent_id = NULL
          FROM res_company pc
         WHERE cc.parent_id = pc.id
     RETURNING cc.id,
               cc.name,
               pc.id,
               pc.name
        """
    )
    if cr.rowcount:
        util.add_to_migration_reports(
            category="Company Hierarchy",
            message="""
                <details>
                    <summary>
                        In Odoo 17, companies with a parent are considered branches
                        of their parent companies, any company that previously had a
                        parent is now set as an independent company to preserve its
                        settings. Therefore the parent company is removed from the
                        following:
                    </summary>
                    <ul>{}</ul>
                </details>
            """.format(
                "".join(
                    f"<li>{name} (id={id}), had as parent company {p_name} (id={p_id})</li>"
                    for id, name, p_id, p_name in cr.fetchall()
                )
            ),
            format="html",
        )
        util.env(cr)["res.company"]._parent_store_compute()
