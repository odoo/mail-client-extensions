from odoo import fields
from odoo.upgrade import util


def migrate(cr, version):
    sale_manager_group_id = util.ref(cr, "sales_team.group_sale_manager")
    if sale_manager_group_id:
        menu_item = util.env(cr).ref("crm.sales_team_menu_team_pipeline", raise_if_not_found=False)
        if menu_item:
            menu_item.group_ids = [fields.Command.unlink(sale_manager_group_id)]
