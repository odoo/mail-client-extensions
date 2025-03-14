from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "industry_fsm_sale.view_project_task_pivot_fsm_inherit_sale")
    util.remove_view(cr, "industry_fsm_sale.view_product_product_kanban_material")
    util.remove_view(cr, "industry_fsm_sale.product_search_form_view_inherit_fsm_sale")
