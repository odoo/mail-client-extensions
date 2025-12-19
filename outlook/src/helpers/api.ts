const api = {
    GET_TRANSLATIONS: '/mail_plugin/get_translations',
    LOG_EMAIL: '/mail_plugin/log_mail_content',
    SEARCH_RECORDS: '/mail_plugin/search_records',
    // Partner
    GET_PARTNER: '/mail_plugin/partner/get',
    SEARCH_PARTNER: '/mail_plugin/search_records/res.partner',
    PARTNER_CREATE: '/mail_plugin/partner/create',
    // CRM Lead
    CREATE_LEAD: '/mail_plugin/lead/create',
    // HELPDESK Ticket
    CREATE_TICKET: '/mail_plugin/ticket/create',
    // Project
    SEARCH_PROJECT: '/mail_plugin/search_records/project.project',
    CREATE_PROJECT: '/mail_plugin/project/create',
    CREATE_TASK: '/mail_plugin/task/create',
    // Authentication
    LOGIN_PAGE: '/web/login', // Should be the usual Odoo login page.
    AUTH_CODE_PAGE: '/mail_plugin/auth', // The page where to allow or deny access. You get an auth code.
    GET_ACCESS_TOKEN: '/mail_plugin/auth/access_token', // The address where to post to exchange an auth code for an access token.
    CHECK_VERSION: '/mail_plugin/auth/check_version',
    OUTLOOK_SCOPE: 'outlook',
    OUTLOOK_FRIENDLY_NAME: 'Outlook',
}

export default api
