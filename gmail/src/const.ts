export const URLS: Record<string, string> = {
    GET_TRANSLATIONS: "/mail_plugin/get_translations",
    LOG_EMAIL: "/mail_plugin/log_mail_content",
    SEARCH_RECORDS: "/mail_plugin/search_records",
    GET_ACTIVITIES: "/mail_plugin/activity/get",
    DONE_ACTIVITY: "/mail_plugin/activity/done",
    CANCEL_ACTIVITY: "/mail_plugin/activity/cancel",
    EDIT_ACTIVITY: "/mail_plugin/activity/edit",
    // Partner
    GET_PARTNER: "/mail_plugin/partner/get",
    SEARCH_PARTNER: "/mail_plugin/search_records/res.partner",
    PARTNER_CREATE: "/mail_plugin/partner/create",
    // CRM Lead
    CREATE_LEAD: "/mail_plugin/lead/create",
    // HELPDESK Ticket
    CREATE_TICKET: "/mail_plugin/ticket/create",
    // Project
    SEARCH_PROJECT: "/mail_plugin/search_records/project.project",
    CREATE_PROJECT: "/mail_plugin/project/create",
    CREATE_TASK: "/mail_plugin/task/create",
};

export const ODOO_AUTH_URLS: Record<string, string> = {
    LOGIN: "/web/login",
    AUTH_CODE: "/mail_plugin/auth",
    CODE_VALIDATION: "/mail_plugin/auth/access_token",
    SCOPE: "outlook",
    FRIENDLY_NAME: "Gmail",
};
