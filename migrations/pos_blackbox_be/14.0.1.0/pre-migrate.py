# -*- coding: utf-8 -*-
from itertools import product

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_model(cr, "pos.order_line_pro_forma", "pos.order_line_pro_forma_be")
    util.rename_model(cr, "pos.order_pro_forma", "pos.order_pro_forma_be")

    accesses = """
        access_pos_order_pro_forma
        access_pos_order_line_pro_forma
        access_minfin_pos_order_pro_forma
        access_minfin_pos_order_line_pro_forma
    """
    for name in util.splitlines(accesses):
        util.rename_xmlid(cr, f"pos_blackbox_be.{name}", f"pos_blackbox_be.{name}_be")

    util.remove_field(cr, "pos.session", "total_rounding_applied")
    util.remove_field(cr, "pos.session", "total_corrections")
    util.remove_field(cr, "pos.session", "amount_of_corrections")
    util.remove_field(cr, "pos.session", "total_discount")
    util.remove_field(cr, "pos.session", "amount_of_discounts")
    util.remove_field(cr, "pos.session", "amount_of_pro_forma_tickets")
    util.remove_field(cr, "pos.session", "amount_of_vat_tickets")

    util.force_noupdate(cr, "pos_blackbox_be.view_pos_session_form", False)

    util.create_column(cr, "pos_config", "certifiedBlackboxIdentifier", "varchar")
    util.remove_field(cr, "pos.config", "blackbox_pos_production_id")
    util.remove_field(cr, "pos.config", "report_sequence_number")
    util.remove_view(cr, "pos_blackbox_be.view_pos_config_kanban_serial_id")

    util.remove_field(cr, "pos.order_pro_forma_be", "hash_chain")
    util.remove_field(cr, "pos.order", "hash_chain")

    # Remove MinFin partner
    minfin_partner = util.ref(cr, "pos_blackbox_be.fdm_minfin")
    if minfin_partner:
        root_partner = util.ref(cr, "base.partner_root")
        util.replace_record_references_batch(cr, {minfin_partner: root_partner}, "res.partner", replace_xmlid=False)
    util.remove_record(cr, "pos_blackbox_be.fdm_minfin")

    util.remove_record(cr, "pos_blackbox_be.minfin_export_orders")

    # Remove report views
    util.remove_view(cr, "pos_blackbox_be.financial_report_template")
    for type_, letter in product({"user", "financial"}, "xz"):
        util.remove_record(cr, f"pos_blackbox_be.action_report_pos_{type_}_{letter}")
        util.remove_view(cr, f"pos_blackbox_be.{type_}_report_template_{letter}")

    # remove view from the merge of the module pos_hr_l10n_be
    util.remove_view(cr, "pos_blackbox_be.hr_employee_pro_forma_view_form")
