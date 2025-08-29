from odoo.upgrade import util


def migrate(cr, version):
    # As 'on_change' base.automation records now take into account the filter_domain field,
    # we need to empty it for the ones that had it before, to ensure the behavior remains the same.
    cr.execute(
        """
        WITH on_change_with_domain_automations AS (
            SELECT id,
                   name->>'en_US' AS name,
                   filter_domain
              FROM base_automation
             WHERE trigger = 'on_change'
               AND filter_domain IS NOT NULL
        )
           UPDATE base_automation
              SET filter_domain = NULL
             FROM on_change_with_domain_automations onchange
            WHERE base_automation.id = onchange.id
        RETURNING onchange.id, onchange.name, onchange.filter_domain
        """,
    )
    if cr.rowcount:
        results = cr.dictfetchall()
        migrated_automations_info = [
            (
                util.get_anchor_link_to_record("base.automation", automation["id"], automation["name"]),
                util.html_escape(automation["filter_domain"]),
            )
            for automation in results
        ]
        migrated_automations_list_items = [
            f'<li>{link} (removed "Apply on" domain: <code>{domain}</code>)</li>'
            for link, domain in migrated_automations_info
        ]
        util.add_to_migration_reports(
            f"""
                <details>
                <summary>
                    Automation rules of trigger type <code>On UI change</code> that had an
                    <code>Apply on</code> filter domain were not using at all their filter domain before
                    the upgrade. Now that they will, the migration script had to empty their filter
                    domain in order to ensure the behavior after the upgrade remains the same.
                    <br/>
                    Here is the list of modified automation rules, in case you want to review them.
                </summary>
                <ul>{"".join(migrated_automations_list_items)}</ul>
                </details>
            """,
            "Automation Rules",
            format="html",
        )
