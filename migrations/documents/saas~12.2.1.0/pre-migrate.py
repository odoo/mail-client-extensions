# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


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
    # some people delete existing folders,
    # however the facets linked to folders (and tags linked to facets) are cascade deleted,
    # but their xmlid stay in database.
    # I know this way of building queries is discouraged (at least!), but I don't know
    # another way to give table name as parameter
    for model in ["documents.facet", "documents.tag", "documents.workflow.rule"]:
        cr.execute(
            """
            DELETE FROM ir_model_data
                  WHERE model = '%(model)s'
                    AND res_id NOT IN (SELECT id
                                         FROM %(table_name)s)
        """
            % {"model": model, "table_name": util.table_of_model(cr, model)}
        )
