from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos.session", "total_tax_a")
    util.remove_field(cr, "pos.session", "total_tax_b")
    util.remove_field(cr, "pos.session", "total_tax_c")
    util.remove_field(cr, "pos.session", "total_tax_d")
    util.remove_field(cr, "pos.session", "total_pro_forma")
    util.remove_field(cr, "pos.session", "total_sold")

    util.remove_field(cr, "pos.order_pro_forma_be", "terminal_id")
    util.remove_field(cr, "pos.order_pro_forma_be", "pos_production_id")
    util.remove_field(cr, "pos.order", "terminal_id")
    util.remove_field(cr, "pos.order", "pos_production_id")

    util.rename_field(cr, "pos.config", "certifiedBlackboxIdentifier", "certified_blackbox_identifier")

    util.remove_field(cr, "hr.employee.public", "insz_or_bis_number")

    util.remove_model(cr, "pos.daily.reports.wizard.be")
    util.remove_record(cr, "pos_blackbox_be.pos_daily_report_be")
    util.remove_menus(cr, [util.ref(cr, "pos_blackbox_be.menu_report_daily_details")])
