from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """Create default access rights for manual transients, maintaining the same rules as before: owner only!"""
    cr.execute(
        """
            WITH new_ima AS (
                INSERT INTO ir_model_access (name, model_id, active, perm_read, perm_write, perm_create, perm_unlink)
                     SELECT 'access_upgrade_default', ir_model.id, true, true, true, true, true
                       FROM ir_model
                  LEFT JOIN ir_model_access
                         ON ir_model_access.model_id = ir_model.id
                      WHERE ir_model.state = 'manual'
                        AND ir_model.transient
                        AND ir_model_access.id IS NULL
                  RETURNING model_id
            ),
            new_rules AS (
                INSERT INTO ir_rule (
                                name, model_id, domain_force, active, global,
                                perm_read, perm_write, perm_create, perm_unlink
                            )
                     SELECT 'Own records only', model_id, '[("create_uid", "=", user.id)]', true, true,
                            true, true, true, true
                       FROM new_ima
                  RETURNING model_id
            )
            SELECT m.id, CONCAT(m.name, ' (', m.model, ')')
              FROM ir_model m
              JOIN new_rules
                ON new_rules.model_id = m.id
        """
    )
    if not cr.rowcount:
        return

    # Create migration report
    model_html_list = "\n".join(
        f"<li>{util.get_anchor_link_to_record('ir.model', id, link_name)}</li>" for id, link_name in cr.fetchall()
    )
    util.add_to_migration_reports(
        f"""
            <details>
                <summary>
                    Transient (aka wizard) models must have defined access rights from version 14.0 and above.
                    Access rights plus record rules allowing access to the record owner were created during upgrade
                    for the following manual transient models:
                </summary>
                <ul>{model_html_list}</ul>
            </details>
            <p><strong>Please make sure to adjust these access rights according to your needs.</strong></p>
        """,
        "Transient models",
        format="html",
    )
