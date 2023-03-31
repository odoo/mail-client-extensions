# -*- coding: utf-8 -*-

import mimetypes
import sys
import uuid
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
    cr.execute(
        """
            SELECT document.id, attachment.name, attachment.mimetype
              FROM documents_document document
              JOIN ir_attachment attachment ON attachment.id = document.attachment_id
             WHERE document.type = 'binary'
        """
    )

    # NOTE
    # `ProcessPoolExecutor.map` arguments needs to be pickleable
    # Functions can only be pickle if they are importable.
    # However, the current file is not importable due to the dash in the filename.
    # We should then put the executed function in its own importable file.
    name = f"_upgrade_{uuid.uuid4().hex}"
    mod = sys.modules[name] = util.import_script(__file__, name=name)

    with ProcessPoolExecutor() as executor:
        execute_batch(
            cr._obj,
            "UPDATE documents_document SET file_extension = %s WHERE id = %s",
            executor.map(mod.extract_extension, cr.fetchall()),
        )
