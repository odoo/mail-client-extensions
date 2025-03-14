from odoo.upgrade import util


def migrate(cr, version):
    for field in {"in_invoice", "out_invoice", "payment", "misc_entry"}:
        util.remove_field(cr, "bank.rec.widget", f"reconciled_{field}_ids")
        util.remove_field(cr, "bank.rec.widget", f"reconciled_{field}_ids_count")
    util.remove_field(cr, "bank.rec.widget", "form_analytic_account_id")
    util.remove_field(cr, "bank.rec.widget", "form_analytic_tag_ids")

    util.remove_field(cr, "bank.rec.widget.line", "analytic_account_id")
    util.remove_field(cr, "bank.rec.widget.line", "analytic_tag_ids")
    util.remove_view(cr, "account_accountant.view_move_form_bank_rec_widget")
