/**
 * Represent a "crm.lead" record.
 */
var Lead = /** @class */ (function () {
    function Lead() {}
    /**
     * Make a RPC call to the Odoo database to create a lead
     * and return the ID of the newly created record.
     */
    Lead.createLead = function (partnerId, emailBody, emailSubject) {
        var url = State.odooServerUrl + URLS.CREATE_LEAD;
        var accessToken = State.accessToken;
        var response = (0, postJsonRpc)(
            url,
            { email_body: emailBody, email_subject: emailSubject, partner_id: partnerId },
            { Authorization: "Bearer " + accessToken },
        );
        return response ? response.lead_id || null : null;
    };
    /**
     * Unserialize the lead object (reverse JSON.stringify).
     */
    Lead.fromJson = function (values) {
        var lead = new Lead();
        lead.id = values.id;
        lead.name = values.name;
        lead.expectedRevenue = values.expectedRevenue;
        lead.probability = values.probability;
        lead.recurringRevenue = values.recurringRevenue;
        lead.recurringPlan = values.recurringPlan;
        return lead;
    };
    /**
     * Parse the dictionary returned by the Odoo database endpoint.
     */
    Lead.fromOdooResponse = function (values) {
        var lead = new Lead();
        lead.id = values.lead_id;
        lead.name = values.name;
        lead.expectedRevenue = values.expected_revenue;
        lead.probability = values.probability;
        if ((0, isTrue)(values.recurring_revenue) && (0, isTrue)(values.recurring_plan)) {
            lead.recurringRevenue = values.recurring_revenue;
            lead.recurringPlan = values.recurring_plan;
        }
        return lead;
    };
    return Lead;
})();
