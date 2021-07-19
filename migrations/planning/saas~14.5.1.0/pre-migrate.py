# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{project_forecast,planning}.planning_view_gantt_no_sample"))
    util.create_column(cr, "planning_slot", "state", "varchar", default="draft")
    cr.execute("UPDATE planning_slot SET state = 'published' where is_published=True")

    def adapter(leaf, _, __):
        left, operator, right = leaf
        operator = "=" if bool(right) else "!="
        return [(left, operator, "published")]

    util.update_field_references(cr, "is_published", "state", only_models=("planning.slot",), domain_adapter=adapter)
    util.remove_field(cr, "planning.slot", "is_published")
