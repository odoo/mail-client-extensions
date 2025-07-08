from odoo.upgrade import util

documents_18_pre_migrate = util.import_script("documents/saas~17.5.1.4/pre-migrate.py")


def migrate(cr, version):
    util.remove_field(cr, "hr.payroll.declaration.mixin", "documents_enabled")
    util.create_column(cr, "res_company", "worker_payroll_folder_id", "int4", fk_table="documents_document")

    with documents_18_pre_migrate.create_documents_fix_token_and_alias(cr):
        # Add a folder to store the payroll documents for workers without a user.
        # It doesn't need to be accessed directly by anyone but admins.
        cr.execute(
            """
            WITH workers_paroll_folder_ids AS (
                INSERT INTO documents_document(
                    name, "type",
                    owner_id, company_id, active,
                    access_internal, access_via_link, is_access_via_link_hidden
                )
                     SELECT '{"en_US": "Workers Payroll"}'::jsonb, 'folder',
                            NULL, c.id, TRUE,
                            'none', 'none', TRUE
                       FROM res_company c
                      WHERE documents_hr_settings
                  RETURNING id, company_id
            ),
            company_update AS (
                UPDATE res_company c
                   SET worker_payroll_folder_id = w.id
                  FROM workers_paroll_folder_ids w
                 WHERE c.id = w.company_id
            )
            UPDATE documents_document d
               SET parent_path = d.id::text || '/'
              FROM workers_paroll_folder_ids w
             WHERE d.id = w.id
            """
        )
