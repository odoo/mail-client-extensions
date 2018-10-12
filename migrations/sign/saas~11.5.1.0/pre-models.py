# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    models = util.splitlines(
        """
        sign{ature,}.request
        sign{ature.request,}.template
        sign{ature,}.request.item
        sign{ature,}.item
        sign{ature,}.item.value
        sign{ature.item.party,.item.role}
        sign{ature,}.item.type
    """
    )
    for model in models:
        util.rename_model(cr, *eb(model))

    util.remove_field(cr, "sign.request", "nb_draft")
    util.rename_field(cr, "sign.request.item", "signature_request_id", "sign_request_id")
    util.rename_field(cr, "sign.template", "signature_item_ids", "sign_item_ids")
    util.rename_field(cr, "sign.template", "signature_request_ids", "sign_request_ids")
    util.rename_field(cr, "sign.item.value", "signature_item_id", "sign_item_id")
    util.rename_field(cr, "sign.item.value", "signature_request_id", "sign_request_id")
