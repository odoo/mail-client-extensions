from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.appraisal", "meeting_ids")
    util.remove_field(cr, "hr.appraisal", "meeting_count_display")
    util.remove_field(cr, "hr.appraisal", "date_final_interview")

    query = "UPDATE hr_appraisal SET active = false WHERE active AND state = 'cancel'"
    util.explode_execute(cr, query, table="hr_appraisal")

    def adapter(leaf, _or, _neg):
        left, op, right = leaf
        prefix, _, _ = left.rpartition(".")
        if prefix:
            prefix += "."
        is_neg = op in [
            "not any",
            "not in",
            "not like",
            "not ilike",
            "not =like",
            "not =ilike",
            "!=",
            "<>",
        ]  # All NEGATIVE_CONDITION_OPERATORS
        to_check = [right] if isinstance(right, str) else right
        if "cancel" not in to_check:
            return [leaf]
        return ["&", leaf, (f"{prefix}active", "=", not is_neg)]

    util.adapt_domains(cr, "hr.appraisal", "state", "state", adapter=adapter)

    util.change_field_selection_values(
        cr, "hr.appraisal", "state", {"new": "1_new", "pending": "2_pending", "done": "3_done", "cancel": "1_new"}
    )

    util.rename_field(cr, "hr.departure.wizard", "cancel_appraisal", "delete_appraisal")
