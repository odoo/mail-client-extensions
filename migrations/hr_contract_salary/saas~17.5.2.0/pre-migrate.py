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
