# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "event_event", "subtitle", "varchar")
    util.create_column(cr, "event_event", "cover_properties", "text")
    cr.execute(
        """
        UPDATE event_event
           SET cover_properties =
                 '{"background-image": "none", "background-color": "oe_blue", "opacity": "0.4", "resize_class": "cover_mid"}'
    """
    )
    # https://github.com/odoo/odoo/issues/49354
    cr.execute("DELETE FROM ir_model_data WHERE module = 'website_event' AND name = 'field_event_event__is_published'")
