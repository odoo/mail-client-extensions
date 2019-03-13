# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "documents_document", "res_id", "int4")
    util.create_column(cr, "documents_document", "request_activity_id", "int4")

    cr.execute(
        """
        UPDATE documents_document d
           SET res_id = a.res_id
          FROM ir_attachment a
         WHERE a.id = d.attachment_id
    """
    )
    cr.execute("DELETE FROM documents_request_wizard")

    # cleanup
    # some avw^wpeople delete existing folders,
    # however the facets linked to folders (and tags linked to facets) are cascade deleted,
    # but their xmlid stay in database.
    cr.execute("""
        DELETE FROM ir_model_data
              WHERE model = 'documents.tag'
                AND res_id NOT IN (SELECT id
                                     FROM documents_tag)
    """)
    cr.execute("""
        DELETE FROM ir_model_data
              WHERE model = 'documents.facet'
                AND res_id NOT IN (SELECT id
                                     FROM documents_facet)
    """)
