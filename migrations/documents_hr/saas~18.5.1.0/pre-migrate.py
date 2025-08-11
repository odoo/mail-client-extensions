from odoo.upgrade import util

documents_18_pre_migrate = util.import_script("documents/saas~17.5.1.4/pre-migrate.py")


def migrate(cr, version):
    # set employee folders = False (make them root) + adapt access rights
    cr.execute(
        """
        UPDATE documents_document d
           SET folder_id = NULL,
               parent_path = d.id::text || '/',
               access_via_link = 'none',
               access_internal = 'none'
          FROM res_company c
         WHERE c.documents_hr_settings
           AND c.documents_employee_folder_id = d.id
        """,
    )

    # update access rights for each employee folders
    # access_ids should not be touched (in case they added some members on the folders, they should keep those members.
    cr.execute(
        """
        UPDATE documents_document d
           SET parent_path = NULL, -- force recompute parent_path of 'self' and children using update_parent_path
               access_via_link = 'edit',
               access_internal = 'none',
               is_access_via_link_hidden = TRUE
          FROM hr_employee e
          JOIN res_company c
            ON c.id = e.company_id
         WHERE c.documents_hr_settings
           AND e.hr_employee_folder_id = d.id
        """,
    )

    with documents_18_pre_migrate.create_documents_fix_token_and_alias(cr):
        # create subfolder 'Contract' under every employee subfolder (it should inherit access rights from the parent)
        util.explode_execute(
            cr,
            cr.mogrify(
                """
            INSERT INTO documents_document (
                name, company_id, "type",
                folder_id, owner_id, active,
                access_internal, access_via_link, is_access_via_link_hidden
            )
            SELECT jsonb_build_object('en_US', 'Contracts'), c.id, 'folder',
                    e.hr_employee_folder_id, NULL, TRUE,
                   'none', 'edit', TRUE
              FROM hr_employee e
              JOIN res_company c
                ON c.id = e.company_id
             WHERE c.documents_hr_settings
               AND e.hr_employee_folder_id IS NOT NULL
               AND {parallel_filter}
            """,
            ).decode(),
            table="hr_employee",
            alias="e",
        )

    # recompute `parent_path` on newly created folders or updated folder_id, assuming that their parent folder has a correct `parent_path` value.
    util.update_parent_path(cr, "documents.document", parent_field="folder_id")

    util.remove_field(cr, "res.config.settings", "documents_hr_folder")
    util.remove_field(cr, "res.company", "documents_hr_folder")

    util.remove_view(cr, "documents_hr.res_users_view_form")
