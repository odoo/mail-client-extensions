from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "event.event_report_template_esc_label_96x82_badge")

    cr.execute("SELECT 4 FROM event_event WHERE badge_format = '96x82' LIMIT 1")
    if cr.rowcount:
        util.force_install_module(cr, "event_iot")
        if util.module_installed(cr, "event_sale"):
            util.force_install_module(cr, "event_sale_iot")
        if util.module_installed(cr, "pos_event"):
            util.force_install_module(cr, "pos_event_iot")
