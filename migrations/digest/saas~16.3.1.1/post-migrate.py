from odoo.upgrade import util


def migrate(cr, version):
    for template_id_suffix in ["mail_layout", "mail_main", "section_mobile", "tool_kpi"]:
        util.if_unchanged(cr, f"digest.digest_{template_id_suffix}", util.update_record_from_xml)
