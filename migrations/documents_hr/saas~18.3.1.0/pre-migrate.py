from odoo.upgrade import util

documents_18_pre_migrate = util.import_script("documents/saas~17.5.1.4/pre-migrate.py")


def migrate(cr, version):
    util.create_column(cr, "res_config_settings", "documents_employee_folder_id", "int4", fk_table="documents_document")
    util.create_column(cr, "res_company", "documents_employee_folder_id", "int4", fk_table="documents_document")
    util.create_column(cr, "hr_employee", "hr_employee_folder_id", "int4", fk_table="documents_document")

    util.remove_field(cr, "hr.departure.wizard", "send_hr_documents_access_link")
    util.remove_field(cr, "hr.departure.wizard", "send_documents_enabled")
    util.remove_field(cr, "hr.departure.wizard", "warning_message")
    util.remove_view(cr, "documents_hr.hr_departure_wizard_view_form")
    util.remove_record(cr, "documents_hr.hr_departure_wizard_action")
    util.delete_unused(cr, "documents_hr.mail_template_document_folder_link")
    util.delete_unused(cr, "documents_hr.ir_actions_server_send_access_link")

    util.create_column(cr, "documents_document", "_upg_employee_id", "int4")

    with documents_18_pre_migrate.create_documents_fix_token_and_alias(cr):
        group_hr_user_id = util.ref(cr, "hr.group_hr_user")

        # Create an Employees folder under "HR" for each company
        cr.execute(
            """
            WITH company_employee_folders AS (
                INSERT INTO documents_document (
                    name, company_id, "type",
                    folder_id, owner_id, active,
                    access_internal, access_via_link, is_access_via_link_hidden
                )
                SELECT jsonb_build_object('en_US', 'Employees'), c.id, 'folder',
                        c.documents_hr_folder, NULL, TRUE,
                       'none', 'none', TRUE
                  FROM res_company c
                 WHERE documents_hr_settings
             RETURNING id AS did, company_id AS cid
            ),
            hr_members_access AS (
                INSERT INTO documents_access (document_id, partner_id, role)
                     SELECT cef.did,
                            u.partner_id,
                           'edit'
                       FROM company_employee_folders cef
                       JOIN res_company_users_rel rcu
                         ON rcu.cid = cef.cid
                       JOIN res_groups_users_rel gu
                         ON rcu.user_id = gu.uid
                       JOIN res_users u
                         ON u.id = gu.uid
                        AND rcu.user_id = u.id
                      WHERE gu.gid = %s
                        AND u.active
           )
           UPDATE res_company c
              SET documents_employee_folder_id = company_employee_folders.did
             FROM company_employee_folders
            WHERE company_employee_folders.cid = c.id
            """,
            [group_hr_user_id],
        )

        # Create a folder for each employee in the new "Employees" folders.
        # Second query as must be parallelized per employee.
        util.explode_execute(
            cr,
            cr.mogrify(
                """
                WITH employees_folders AS (
                    INSERT INTO documents_document (
                            _upg_employee_id, type, name, company_id, folder_id,
                            access_internal, access_via_link, is_access_via_link_hidden,
                            active
                        )
                         SELECT e.id,
                                'folder',
                                jsonb_build_object('en_US', e.name),
                                e.company_id AS company_id,
                                c.documents_employee_folder_id AS folder_id,
                                'none',
                                'none',
                                TRUE,
                                TRUE
                           FROM hr_employee e
                           JOIN res_company c
                             ON c.id = e.company_id
                          WHERE c.documents_employee_folder_id IS NOT NULL
                            AND {parallel_filter}
                      RETURNING id as did,
                                folder_id as fid,
                                company_id as cid,
                                _upg_employee_id as eid
                ),
                hr_members_access AS (
                    INSERT INTO documents_access (document_id, partner_id, role)
                         SELECT ef.did,
                                u.partner_id,
                                'edit'
                           FROM employees_folders ef
                           JOIN res_company_users_rel rcu
                             ON rcu.cid = ef.cid
                           JOIN res_groups_users_rel gu
                             ON rcu.user_id = gu.uid
                           JOIN res_users u
                             ON u.id = gu.uid
                            AND rcu.user_id = u.id
                          WHERE gu.gid = %s
                            AND u.active
                )
                UPDATE hr_employee e
                   SET hr_employee_folder_id = ef.did
                  FROM employees_folders ef
                 WHERE e.id = ef.eid
                """,
                [group_hr_user_id],
            ).decode(),
            table="hr_employee",
            alias="e",
        )

        # recompute `parent_path` on newly created folders, assuming that their parent folder has a correct `parent_path` value.
        query = """
            WITH _new_folders AS (
                   SELECT c.documents_employee_folder_id AS fid
                     FROM res_company c
                    WHERE c.documents_employee_folder_id IS NOT NULL
                    UNION
                   SELECT e.hr_employee_folder_id AS fid
                     FROM hr_employee e
                    WHERE e.hr_employee_folder_id IS NOT NULL
            ),
            _compute_parent_path AS (
                SELECT d.id, CONCAT(f.parent_path, d.id, '/') as path
                  FROM documents_document d
                  JOIN _new_folders n
                    ON n.fid = d.id
             LEFT JOIN documents_document f
                    ON f.id = d.folder_id
            )
            UPDATE documents_document d
               SET parent_path = c.path
              FROM _compute_parent_path c
             WHERE c.id = d.id
        """
        # no need to explode the query as there shouldn't have millions of company or employee records.
        cr.execute(query)

        # Move all employee documents to their new specific folder
        # (without changing existing access rights)
        util.explode_execute(
            cr,
            """
            UPDATE documents_document d
               SET folder_id = e.hr_employee_folder_id,
                   parent_path = f.parent_path || d.id::text || '/'
              FROM res_company c
              JOIN hr_employee e
                ON e.company_id = c.id
              JOIN documents_document f
                ON e.hr_employee_folder_id = f.id
             WHERE d.folder_id = c.documents_hr_folder
               AND e.work_contact_id = d.partner_id
               AND {parallel_filter}
            """,
            alias="d",
            table="documents_document",
        )

        # fix parent paths of employee folders' folder children's children,
        # i.e., documents whose parent is a child of an employee folder.
        cr.execute(
            """
            WITH RECURSIVE parent_paths AS (
                SELECT f.id,
                       f.parent_path
                  FROM documents_document f
                  JOIN hr_employee e
                    ON e.hr_employee_folder_id = f.id
                 WHERE type = 'folder'
                 UNION
                SELECT d.id,
                       p.parent_path || d.id || '/' AS parent_path
                  FROM documents_document AS d
                  JOIN parent_paths AS p
                    ON d.folder_id = p.id
            )
            UPDATE documents_document
               SET parent_path = parent_paths.parent_path
              FROM parent_paths
             WHERE parent_paths.id = documents_document.id
            """
        )
