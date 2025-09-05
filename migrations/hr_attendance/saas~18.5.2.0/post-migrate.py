def migrate(cr, version):
    # Create 1 ruleset by company
    cr.execute("""
        INSERT INTO hr_attendance_overtime_ruleset (
                name, country_id, company_id, rate_combination_mode
            )
            SELECT 'Legacy Rules',
                   ctry.id,
                   c.id,
                   'max'
            FROM res_company c
            JOIN res_partner p ON c.partner_id = p.id
            JOIN res_country ctry ON p.country_id = ctry.id
            WHERE c.active
    """)
    # On every ruleset: employee schedule rule
    cr.execute("""
        INSERT INTO hr_attendance_overtime_rule (
            name, base_off, expected_hours_from_contract, ruleset_id, paid
        )
             SELECT 'Rule Schedule Hours',
                    'quantity',
                    TRUE,
                    rs.id,
                    TRUE
               FROM hr_attendance_overtime_ruleset rs
    """)
    # On every ruleset: non work days
    cr.execute("""
        INSERT INTO hr_attendance_overtime_rule (
            name, base_off, ruleset_id, paid,
            timing_type, timing_start, timing_stop
        )
             SELECT 'Rule Schedule Hours',
                    'timing',
                    rs.id,
                    TRUE,
                    'non_work_days',
                    0.0,
                    24.0
               FROM hr_attendance_overtime_ruleset rs
    """)
    # Put the ruleset on every version
    cr.execute("""
        UPDATE hr_version
           SET ruleset_id = rs.id
          FROM hr_attendance_overtime_ruleset rs
         WHERE hr_version.company_id = rs.company_id
    """)
