/**
 * Represent an error and translate its code to a message.
 */

const _ERROR_CODE_MESSAGES: Record<string, string> = {
    http_error_odoo: "Could not connect to database. Try to log out and in.",
    insufficient_credit: "You don't have enough credit to enrich.",
    company_created: "Company Created.",
    // IAP
    http_error_iap: "Our IAP server is down, please come back later.",
    exhausted_requests:
        "Oops, looks like you have exhausted your free enrichment requests. Please log in to try again.",
    missing_data: "No data found for this email address.",
    unknown: "Something bad happened. Please, try again later.",
};

/**
 * Represent an error message which will be displayed on the add-on.
 * Translate the code into a message to display to the user.
 */
export class ErrorMessage {
    code: string;
    message: string;
    information: string;

    // False if the error means that we can not contact the Odoo database
    // (e.g. HTTP error)
    canContactOdooDatabase: boolean = true;

    canCreateCompany: boolean = true;

    constructor(code: string = null, information: any = null) {
        if (code) {
            this.setError(code, information);
        }
    }

    /**
     * Set the code error and find the appropriate message to display.
     */
    setError(code: string, information: any = null) {
        if (code === "no_data") {
            code = "missing_data";
            information = null;
        }

        this.code = code;
        this.information = information;
        this.message = _ERROR_CODE_MESSAGES[this.code];

        if (code === "http_error_odoo") {
            this.canContactOdooDatabase = false;
        }
    }

    /**
     * Unserialize the error object (reverse JSON.stringify).
     */
    static fromJson(values: any) {
        const error = new ErrorMessage();
        error.code = values.code;
        error.message = values.message;
        error.canContactOdooDatabase = values.canContactOdooDatabase;
        error.canCreateCompany = values.canCreateCompany;
        error.information = values.information;
        return error;
    }
}
