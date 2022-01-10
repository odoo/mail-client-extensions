# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_html(cr, "crm.lead", "description")
    util.rename_field(cr, "crm.lead", "meeting_count", "calendar_event_count")
    cr.execute(
        r"""
        DELETE FROM ir_translation
              WHERE type = 'model_terms'
                AND name = 'ir.ui.view,arch_db'
                AND src LIKE '%%meeting\_count%%'
                AND res_id = %s
          RETURNING id
        """,
        [util.ref(cr, "crm.crm_lead_view_form")],
    )
