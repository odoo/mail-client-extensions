from odoo.upgrade import util


def migrate(cr, version):
    xmlids = [
        "l10n_ma_hr_payroll.hr_contract_type_emp",
        "l10n_ma_hr_payroll.hr_contract_type_wrkr",
        "l10n_ma_hr_payroll.hr_contract_type_sub",
    ]
    ids = [util.ref(cr, xmlid) for xmlid in xmlids]
    cr.execute(
        """
    UPDATE hr_version v
       SET employee_type = CASE v.contract_type_id
                              WHEN %s THEN 'employee'
                              WHEN %s THEN 'worker'
                              WHEN %s THEN 'contractor'
                           END
     WHERE v.contract_type_id IN %s
    """,
        (*ids, tuple(ids)),
    )
    for xmlid in xmlids:
        util.remove_record(cr, xmlid)
