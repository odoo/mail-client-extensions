# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    # sdd_mandate original_doc must be converted to ir.attachment
    util.convert_binary_field_to_attachment(cr, "sdd.mandate", "original_doc", name_field="original_doc_filename")
    # disconnect the attachment from the field
    cr.execute(
        "UPDATE ir_attachment SET res_field = NULL WHERE res_model = 'sdd.mandate' AND res_field = 'original_doc'"
    )

    util.remove_field(cr, "sdd.mandate", "original_doc")
    util.remove_field(cr, "sdd.mandate", "original_doc_filename")

    """ create sdd_scheme columns & set default value """
    util.create_column(cr, "sdd_mandate", "sdd_scheme", "varchar")
    cr.execute("UPDATE sdd_mandate SET sdd_scheme = 'CORE'")
    util.create_column(cr, "account_batch_payment", "sdd_scheme", "varchar")
    cr.execute("UPDATE account_batch_payment SET sdd_scheme = 'CORE'")
