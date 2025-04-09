from odoo.upgrade import util


def migrate(cr, version):
    # Move all the payroll documents (not folders) to their related employees My Drive.
    # My drive is the folder with `folder_id = False` and `owner_id = user_id`
    util.explode_execute(
        cr,
        """
        WITH moved_documents AS (
            UPDATE documents_document d
               SET folder_id = CASE WHEN e.user_id IS NULL THEN c.worker_payroll_folder_id END,
                   owner_id = e.user_id,
                   partner_id = e.work_contact_id
              FROM res_company c
              JOIN hr_employee e
                ON e.company_id = c.id
         LEFT JOIN res_users u
                ON e.user_id = u.id
             WHERE d.folder_id = c.documents_payroll_folder_id
               AND e.active
               AND u.active
               AND e.work_contact_id = d.partner_id
               AND d.type != 'folder' -- if removed, parent_path update has to propagate to children
               AND {parallel_filter}
         RETURNING d.id AS document_id, d.folder_id AS folder_id
        )
        UPDATE documents_document d
           SET parent_path = COALESCE(f.parent_path, '') || d.id::text || '/'
          FROM moved_documents m
     LEFT JOIN documents_document f
            ON f.id = m.folder_id
         WHERE d.id = m.document_id
        """,
        alias="d",
        table="documents_document",
    )

    # Rename the payroll folder as it could contain other files and has configured access rights
    cr.execute(
        """
        UPDATE documents_document d
           SET name = '{"en_US": "Payroll (old)"}'::jsonb
         WHERE id IN (SELECT documents_payroll_folder_id FROM res_company)
        """
    )

    util.remove_field(cr, "res.config.settings", "documents_payroll_folder_id")
    util.remove_field(cr, "res.company", "documents_payroll_folder_id", drop_column=True)
    util.if_unchanged(cr, "documents_hr_payroll.mail_template_new_declaration", util.update_record_from_xml)
