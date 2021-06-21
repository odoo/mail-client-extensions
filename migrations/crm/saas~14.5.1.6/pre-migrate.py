# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_references(
        cr, "activity_date_deadline_my", "my_activity_date_deadline", only_models=("crm.lead",)
    )
    util.remove_field(cr, "crm.lead", "activity_date_deadline_my")
