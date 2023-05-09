# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "documents_hr.mail_template_document_folder_link")

    util.explode_execute(
        cr,
        """
            UPDATE documents_document d
               SET partner_id = e.work_contact_id
              FROM hr_employee e
             WHERE d.partner_id = e.address_home_id
        """,
        table="documents_document",
        alias="d",
    )
