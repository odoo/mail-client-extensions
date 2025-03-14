from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE documents_document
           SET url = 'https://' || url
         WHERE url IS NOT NULL
           AND NOT starts_with(url, 'https://')
           AND NOT starts_with(url, 'http://')
           AND NOT starts_with(url, 'ftp://')
        """,
        table="documents_document",
    )
