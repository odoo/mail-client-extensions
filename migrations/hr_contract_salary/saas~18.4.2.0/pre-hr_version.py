from odoo.upgrade import util


def set_personal_info_to_version(cr, module: str, xmlids: list[str]):
    if any("." in name for name in xmlids):
        raise util.SleepyDeveloperError("xmlids should be the name part")

    query = """
        WITH _fields AS (
            SELECT i.id as info_id,
                   nf.id as field_id
              FROM hr_contract_salary_personal_info i
              JOIN ir_model_data x
                ON x.model = 'hr.contract.salary.personal.info'
               AND x.res_id = i.id
              JOIN ir_model_fields of
                ON of.id = i.res_field_id
              JOIN ir_model_fields nf
                ON nf.model = 'hr.version'
               AND nf.name = of.name
             WHERE i.applies_on = 'employee'
               AND x.module = %s
               AND x.name IN %s
        )
        UPDATE hr_contract_salary_personal_info i
           SET applies_on = 'version_personal',
               res_field_id = f.field_id
          FROM _fields f
         WHERE f.info_id = i.id
    """
    cr.execute(query, [module, tuple(xmlids)])


def migrate(cr, version):
    xmlids = """
        hr_contract_salary_personal_info_sex
        hr_contract_salary_personal_info_country_id
        hr_contract_salary_personal_info_identification_id
        hr_contract_salary_personal_info_street
        hr_contract_salary_personal_info_street2
        hr_contract_salary_personal_info_city
        hr_contract_salary_personal_info_zip
        hr_contract_salary_personal_info_state_id
        hr_contract_salary_personal_info_country
    """
    set_personal_info_to_version(cr, "hr_contract_salary", list(util.splitlines(xmlids)))
