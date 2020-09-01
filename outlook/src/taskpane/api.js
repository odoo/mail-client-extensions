const api = {
    baseURL: localStorage.getItem('baseURL'),
    //createLead: "/mail_client_extension/lead/create",
    getLeads: "/mail_client_extension/lead/get_by_partner_id",
    //deleteLead: "/mail_client_extension/lead/delete",
    getPartner: "/mail_client_extension/partner/get",
    logMail: "/mail_client_extension/log_single_mail_content",
    getInstalledModules: "/mail_client_extension/modules/get",
    contactCreate: '/mail_client_extension/partner/create',
    redirectCreateLead: "/mail_client_extension/lead/create_from_partner",
    iapLeadEnrichmentEmail: "https://iap-services.odoo.com/iap/clearbit/1/lead_enrichment_email", // TODO remove
    iapLeadEnrichment: "https://iap-services.odoo.com/iap/mail_extension/enrich",

    // Authentication
    loginPage: "/web/login", // Should be the usual Odoo login page.
    authCodePage: "/mail_client_extension/auth", // The page where to allow or deny access. You get an auth code.
    getAccessToken: "/mail_client_extension/auth/access_token", // The address where to post to exchange an auth code for an access token.
    addInRedirect: "https://" + __DOMAIN__ + "/taskpane.html", // The address of the outlook add-in to redirect to at the end of the auth flow. See the webpack.config.js for the __DOMAIN__ variable.
    outlookScope: "outlook",
    outlookFriendlyName: "Outlook",
};

export default api;