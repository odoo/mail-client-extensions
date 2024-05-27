def migrate(cr, version):
    cr.execute(r"""
    WITH bl as (
       delete from ir_config_parameter
             where key = 'hr_recruitment.blacklisted_emails'
         returning value
    ), emails as (
       SELECT regexp_split_to_table(trim(value), '\s*,\s*') as email
         FROM bl
       EXCEPT
       SELECT email
         FROM hr_job_platform
    )
    INSERT INTO hr_job_platform(name, email, regex)
    SELECT 'Blacklisted email ' || row_number() over (), email, '(?!)'
    FROM emails
   """)
