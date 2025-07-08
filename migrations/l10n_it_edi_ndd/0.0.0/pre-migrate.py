from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("17.0", "saas~18.1"):
        check_and_report_duplicates(cr)


def check_and_report_duplicates(cr):
    cr.execute("""
        WITH duplicates AS (
            SELECT id,
                   code,
                   ROW_NUMBER() OVER (PARTITION BY code ORDER BY id) AS rn
              FROM l10n_it_document_type
        ),
        to_update AS (
            SELECT id,
                   code || '_' || id AS new_code
              FROM duplicates
             WHERE rn > 1
        )
        UPDATE l10n_it_document_type t
           SET code = u.new_code
          FROM to_update u
         WHERE t.id = u.id
     RETURNING t.id, t.name->>'en_US'
    """)

    updated_records = cr.fetchall()
    if updated_records:
        util.add_to_migration_reports(
            """
            <details>
                <summary>
                During the migration, we found duplicate codes in <code>l10n_it.document.type</code> records.
                To allow the upgrade to complete successfully, we updated these codes to make them unique.
                We recommend reviewing the changes and updating the corresponding records in your database if needed.
                </summary>
                <ul>{}</ul>
            </details>
            """.format(
                " ".join(
                    "<li>{}</li>".format(util.get_anchor_link_to_record("l10n_it.document.type", id, name))
                    for id, name in updated_records
                )
            ),
            category="Duplicate Document Type Codes",
            format="html",
        )
