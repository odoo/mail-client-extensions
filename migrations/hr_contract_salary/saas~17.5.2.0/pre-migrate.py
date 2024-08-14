from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "generate.simulation.link")

    util.create_column(cr, "hr_contract_salary_offer", "validity_days_count", "integer")
    util.explode_execute(
        cr,
        """
        UPDATE hr_contract_salary_offer
           SET validity_days_count = offer_end_date - DATE(create_date)
         WHERE offer_end_date IS NOT NULL
        """,
        table="hr_contract_salary_offer",
    )

    util.rename_field(cr, "hr.contract.salary.benefit.value", "color", "selector_highlight")
    util.change_field_selection_values(cr, "hr.contract.salary.benefit.value", "selector_highlight", {"green": "none"})
    util.remove_field(cr, "hr.contract.salary.benefit", "impacts_net_salary")
    util.create_column(cr, "hr_contract_salary_benefit", "always_show_description", "boolean", default=True)
    cr.execute("""
    UPDATE hr_contract_salary_benefit
       SET always_show_description=FALSE
     WHERE hide_description=TRUE""")
    util.remove_field(cr, "hr.contract.salary.benefit", "hide_description")
    util.create_column(cr, "hr_contract_salary_benefit_value", "always_show_description", "boolean", default=True)
    cr.execute("""
    UPDATE hr_contract_salary_benefit_value
       SET always_show_description=FALSE
     WHERE hide_description=TRUE""")
    util.remove_field(cr, "hr.contract.salary.benefit.value", "hide_description")
