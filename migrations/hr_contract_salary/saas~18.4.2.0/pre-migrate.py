from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE hr_version v
           SET active = True
          FROM hr_version_sign_request_rel rel
          JOIN sign_request s
            ON s.id = rel.sign_request_id
          JOIN hr_contract_salary_offer_sign_request_rel off_rel
            ON off_rel.sign_request_id = s.id
          JOIN hr_contract_salary_offer o
            ON o.id = off_rel.hr_contract_salary_offer_id
         WHERE NOT v.active
           AND v.id = rel.hr_version_id
           AND s.nb_closed = 1
           AND o.state = 'half_signed'
        """
    )

    util.rename_field(cr, "hr.job", "default_contract_id", "contract_template_id")
    util.rename_field(cr, "hr.contract.salary.offer", "employee_contract_id", "employee_version_id")
    util.rename_field(cr, "hr.version", "origin_contract_id", "origin_version_id")
    util.rename_field(cr, "hr.version", "default_contract_id", "contract_template_id")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_contract_salary.hr_contract_salary_personal_info_{gender,sex}"))
    util.rename_xmlid(cr, *eb("hr_contract_salary.hr_contract_salary_personal_info_{gender,sex}_male"))
    util.rename_xmlid(cr, *eb("hr_contract_salary.hr_contract_salary_personal_info_{gender,sex}_female"))
    util.rename_xmlid(cr, *eb("hr_contract_salary.hr_contract_salary_personal_info_{gender,sex}_other"))
    # demo data
    util.rename_xmlid(cr, *eb("hr_contract_salary.{hr_contract,contract_template}_cdi_experienced_developer"))

    util.remove_record(cr, "hr_contract_salary.ir_cron_clean_redundant_salary_data")
    util.remove_view(cr, "hr_contract_salary.contract_employee_report_view_pivot_inherit")

    util.change_field_selection_values(cr, "hr.contract.salary.resume", "value_type", {"contract": "version"})
