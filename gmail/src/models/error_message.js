/**
 * Represent an error and translate its code to a message.
 */
var _ERROR_CODE_MESSAGES = {
    odoo: null,
    http_error_odoo: "Could not connect to database. Try to log out and in.",
    insufficient_credit: "Not enough credits to enrich.",
    company_created: null,
    company_updated: null,
    // IAP
    http_error_iap: "Our IAP server is down, please come back later.",
    exhausted_requests:
        "Oops, looks like you have exhausted your free enrichment requests. Please log in to try again.",
    missing_data: "No insights found for this address",
    unknown: "Something bad happened. Please, try again later.",
    // Attachment
    attachments_size_exceeded:
        "Attachments could not be logged in Odoo because their total size exceeded the allowed maximum.",
};
/**
 * Represent an error message which will be displayed on the add-on.
 * Translate the code into a message to display to the user.
 */
var ErrorMessage = /** @class */ (function () {
    function ErrorMessage(code, information) {
        if (code === void 0) {
            code = null;
        }
        if (information === void 0) {
            information = null;
        }
        // False if the error means that we can not contact the Odoo database
        // (e.g. HTTP error)
        this.canContactOdooDatabase = true;
        this.canCreateCompany = true;
        if (code) {
            this.setError(code, information);
        }
    }
    /**
     * Set the code error and find the appropriate message to display.
     */
    ErrorMessage.prototype.setError = function (code, information) {
        if (information === void 0) {
            information = null;
        }
        if (code === "no_data") {
            code = "missing_data";
            information = null;
        }
        this.code = code;
        this.information = information;
        this.message = (0, _t)(_ERROR_CODE_MESSAGES[this.code]);
        if (code === "http_error_odoo") {
            this.canContactOdooDatabase = false;
        }
    };
    /**
     * Unserialize the error object (reverse JSON.stringify).
     */
    ErrorMessage.fromJson = function (values) {
        var error = new ErrorMessage();
        error.code = values.code;
        error.message = values.message;
        error.canContactOdooDatabase = values.canContactOdooDatabase;
        error.canCreateCompany = values.canCreateCompany;
        error.information = values.information;
        return error;
    };
    return ErrorMessage;
})();
