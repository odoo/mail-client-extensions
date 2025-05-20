from odoo.upgrade import util


def migrate(cr, version):
    util.make_field_non_stored(cr, "hr.employee", "spouse_fiscal_status")
    util.make_field_non_stored(cr, "hr.employee", "disabled_spouse_bool")
    util.make_field_non_stored(cr, "hr.employee", "disabled_children_bool")
    util.make_field_non_stored(cr, "hr.employee", "disabled_children_number")
    util.make_field_non_stored(cr, "hr.employee", "l10n_be_dependent_children_attachment")
    util.make_field_non_stored(cr, "hr.employee", "other_dependent_people")
    util.make_field_non_stored(cr, "hr.employee", "other_senior_dependent")
    util.make_field_non_stored(cr, "hr.employee", "other_disabled_senior_dependent")
    util.make_field_non_stored(cr, "hr.employee", "other_juniors_dependent")
    util.make_field_non_stored(cr, "hr.employee", "other_disabled_juniors_dependent")
    util.make_field_non_stored(cr, "hr.employee", "fiscal_voluntarism")
