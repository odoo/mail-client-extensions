/**
 * Represent an error and translate its code to a message.
 */

// TODO: translate
const _ERROR_CODE_MESSAGES: Record<string, string> = {
    odoo: null, // Message is contained in the additional information
    http_error_odoo: "Could not connect to database. Try to log out and in.",
    unknown: "Something bad happened. Please, try again later.",
    // Attachment
    attachments_size_exceeded:
        "Attachments could not be logged in Odoo because their total size exceeded the allowed maximum.",
};

/**
 * Represent an error message which will be displayed on the add-on.
 * Translate the code into a message to display to the user.
 */
export class ErrorMessage {
    code: string;
    message: string;
    information: string;

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
        this.message = information || _ERROR_CODE_MESSAGES[this.code];
    }

    /**
     * Unserialize the error object (reverse JSON.stringify).
     */
    static fromJson(values: any) {
        const error = new ErrorMessage();
        error.code = values.code;
        error.message = values.message;
        error.information = values.information;
        return error;
    }
}
