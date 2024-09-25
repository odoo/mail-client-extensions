from odoo.upgrade import util

documents_pre_migrate = util.import_script("documents/saas~17.5.1.4/pre-migrate.py")


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "documents_hr.documents_hr_documents_absences",
        "documents_hr.documents_tag_absences",
    )
    util.rename_xmlid(
        cr,
        "documents_hr.documents_hr_documents_employees",
        "documents_hr.documents_tag_employees",
    )
    util.rename_xmlid(
        cr,
        "documents_hr.documents_hr_documents_Cerification",
        "documents_hr.documents_tag_certification",
    )

    util.remove_field(cr, "hr.employee", "documents_share_id")
    util.create_column(cr, "documents_redirect", "employee_id", "int4")

    # We can create and send a share to a user we archived, so he can still download
    # its file, we want to migrate those share, and so we insert new rows in the
    # temporary table `documents_redirect`.
    cr.execute(
        """
     INSERT INTO documents_redirect (document_id, access_token, employee_id) (
          SELECT DISTINCT ON (share.id)
                 NULL,
                 share.access_token,
                 empl.id
            FROM documents_share AS share
            JOIN res_users AS usr
              ON usr.partner_id = share.owner_id
            JOIN hr_employee AS empl
              ON empl.user_id = usr.id
           WHERE share.type = 'domain'
             AND share.domain = ($$[('owner_id', '=', $$ || usr.id || ')]')
        )
         """
    )

    documents_pre_migrate.migrate_folders_xmlid(
        cr,
        "documents_hr",
        {
            "documents_hr_folder": "document_hr_folder",
        },
    )
