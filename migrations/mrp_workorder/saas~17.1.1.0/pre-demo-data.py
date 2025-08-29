from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT 1 FROM ir_module_module WHERE demo AND name='mrp_workorder'")
    if not cr.rowcount:
        xml_ids = util.splitlines("""
            mrp.product_product_computer_desk
            mrp.product_product_computer_desk_head
            mrp.product_product_computer_desk_leg
            mrp.mrp_inventory_1
            mrp.mrp_inventory_2
            mrp.mrp_bom_desk
            mrp.mrp_bom_desk_line_1
            mrp.mrp_bom_desk_line_2
            mrp.mrp_production_3
            mrp.mrp_workcenter_3
            mrp.mrp_routing_workcenter_5
            mrp_workorder.quality_point_register_serial_production
            mrp_workorder.quality_point_component_registration
            mrp_workorder.quality_point_instructions
            mrp_workorder.quality_point_component_registration_2
            mrp_workorder.quality_point_register_production
            mrp_workorder.quality_point_print_labels
        """)
        for xml_id in xml_ids:
            if xml_id.startswith("mrp_workorder."):
                util.rename_xmlid(cr, xml_id.replace("mrp_workorder.", "mrp."), xml_id)
            util.force_noupdate(cr, xml_id, noupdate=True)
