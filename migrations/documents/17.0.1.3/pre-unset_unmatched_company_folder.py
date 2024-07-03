from odoo.upgrade import util


def migrate(cr, version):
    # Users could restrict shared folders originally accessible to multiple companies.
    # This patch resolves the issue by making document folders shared again
    # When they are already being used by different companies.

    fields = [
        "account_folder",
        "documents_hr_folder",
        "documents_payroll_folder_id",
        "recruitment_folder_id",
        "product_folder",
        "documents_spreadsheet_folder_id",
    ]

    query = """
             WITH folder_info AS (
                SELECT df.id,
                       rc2.name AS folder_company_name,
                       array_agg(rc.name) AS company_names
                 FROM documents_folder df
                 JOIN res_company rc
                   ON df.id = rc.{field}
                 JOIN res_company rc2
                   ON df.company_id = rc2.id
                WHERE df.company_id != rc.id
                GROUP BY df.id, rc2.name
         ) UPDATE documents_folder AS df
              SET company_id = NULL
             FROM folder_info fi
            WHERE df.id = fi.id
        RETURNING df.id, df.name->>'en_US', fi.folder_company_name, fi.company_names
    """

    changed_workspaces = []
    for field in fields:
        if util.column_exists(cr, "res_company", field):
            cr.execute(util.format_query(cr, query, field=field))
            if cr.rowcount:
                changed_workspaces.extend(cr.fetchall())

    if changed_workspaces:
        util.add_to_migration_reports(
            message="""
            <details>
                <summary>
                    Some companies were using Document Folders from other companies,
                    which is not allowed. To allow the upgrade to continue, those
                    document-centralizing folders were made shared across companies.
                    Below is the full list of updated records:
                </summary>
                <ul>{}</ul>
            </details>
            """.format(
                "\n".join(
                    "<li>{} was used by company(ies) {} but was restricted to company {}</li>".format(
                        util.get_anchor_link_to_record("documents.folder", folder_id, folder_name),
                        ", ".join(map(repr, company_names)),
                        folder_company_name,
                    )
                    for folder_id, folder_name, folder_company_name, company_names in changed_workspaces
                )
            ),
            category="Documents folder",
            format="html",
        )
