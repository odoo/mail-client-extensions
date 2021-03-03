# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "website_visitor", "has_push_notifications", "bool")
    cr.execute(
        """
        UPDATE website_visitor
           SET has_push_notifications = TRUE
         WHERE push_token IS NOT NULL
    """
    )
