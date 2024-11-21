from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "documents_fleet.ir_actions_server_link_to_vehicule")
