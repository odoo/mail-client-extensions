const URLS: Record<string, string> = {
    GET_TRANSLATIONS: "/mail_plugin/get_translations",
    LOG_EMAIL: "/mail_plugin/log_mail_content",
    // Partner
    GET_PARTNER: "/mail_plugin/partner/get",
    SEARCH_PARTNER: "/mail_plugin/partner/search",
    PARTNER_CREATE: "/mail_plugin/partner/create",
    ENRICH_COMPANY: "/mail_plugin/partner/enrich_and_create_company",
    // CRM Lead
    CREATE_LEAD: "/mail_plugin/lead/create",
    // HELPDESK Ticket
    CREATE_TICKET: "/mail_plugin/ticket/create",
    // IAP
    IAP_COMPANY_ENRICHMENT: "https://iap-services.odoo.com/iap/mail_extension/enrich",
};

const ODOO_AUTH_URLS: Record<string, string> = {
    LOGIN: "/web/login",
    AUTH_CODE: "/mail_plugin/auth",
    CODE_VALIDATION: "/mail_plugin/auth/access_token",
    SCOPE: "outlook",
    FRIENDLY_NAME: "Gmail",
};
