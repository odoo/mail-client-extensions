from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "project_task", "partner_name", "varchar")
    util.create_column(cr, "project_task", "partner_phone", "varchar")
    util.create_column(cr, "project_task", "partner_company_name", "varchar")

    query = """
        UPDATE project_task t
           SET partner_name = p.name,
               partner_phone = p.phone,
               partner_company_name = p.company_name
          FROM res_partner p
         WHERE p.id = t.partner_id
    """
    util.explode_execute(cr, query, table="project_task", alias="t")
