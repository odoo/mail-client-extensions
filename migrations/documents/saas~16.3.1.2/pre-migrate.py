import mimetypes
from concurrent.futures import ProcessPoolExecutor

from psycopg2.extras import execute_batch

from odoo.tools.mimetypes import get_extension

from odoo.upgrade import util


def extract_extension(document_info):
    """Compute the file extension from the document information.

    :param tuple document_info: document information as a tuple (document_id, name, mimetype)
    :return tuple: extension for the document as a tuple (extension, document_id)
    """
    document_id, name, mimetype = document_info
    name = name or ""
    mimetype_from_name = mimetypes.guess_type(name)[0]
    mimetype = mimetype or mimetype_from_name

    extension = get_extension(name) if mimetype == mimetype_from_name else mimetypes.guess_extension(mimetype)
    extension = extension.lstrip(".") if extension else None
    return extension, document_id


def migrate(cr, version):
    util.create_column(cr, "documents_document", "is_multipage", "boolean", default=False)  # Skip _compute

    util.create_column(cr, "documents_document", "file_extension", "varchar")

    with ProcessPoolExecutor() as executor, util.named_cursor(cr) as ncr:
        ncr.execute(
            """
            SELECT document.id, attachment.name, attachment.mimetype
              FROM documents_document document
              JOIN ir_attachment attachment ON attachment.id = document.attachment_id
             WHERE document.type = 'binary'
            """
        )
        while chunk := ncr.fetchmany(100000):  # fetchall() could cause MemoryError
            chunksize = 1000
            execute_batch(
                cr._obj,
                "UPDATE documents_document SET file_extension = %s WHERE id = %s",
                executor.map(util.make_pickleable_callback(extract_extension), chunk, chunksize=chunksize),
                page_size=chunksize,
            )
