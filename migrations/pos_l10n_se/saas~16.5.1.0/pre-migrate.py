from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "pos.order_line_pro_forma")
    util.remove_model(cr, "pos.order_pro_forma")
    util.remove_field(cr, "pos.order", "is_refund")
    util.rename_field(cr, "pos.order", "blackbox_tax_category_a", "sweden_blackbox_tax_category_a")
    util.rename_field(cr, "pos.order", "blackbox_tax_category_b", "sweden_blackbox_tax_category_b")
    util.rename_field(cr, "pos.order", "blackbox_tax_category_c", "sweden_blackbox_tax_category_c")
    util.rename_field(cr, "pos.order", "blackbox_tax_category_d", "sweden_blackbox_tax_category_d")
    util.rename_field(cr, "pos.order", "blackbox_unit_id", "sweden_blackbox_unit_id")
    util.rename_field(cr, "pos.order", "blackbox_signature", "sweden_blackbox_signature")
    util.rename_field(cr, "pos.order", "blackbox_device", "sweden_blackbox_device")
    util.remove_field(cr, "pos.config", "proformat_sequence")
    util.remove_model(cr, "pos.daily.reports.wizard")
    util.rename_field(cr, "account.tax", "identification_letter", "sweden_identification_letter")
    util.remove_view(cr, "l10n_se_pos_cert.view_pos_order_pro_forma_tree")
