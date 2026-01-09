/**
 * Represent an error and translate its code to a message.
 */

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
    private message: string;

    constructor(code: string = null, information: any = null) {
        this.code = code;
        this.message = information || _ERROR_CODE_MESSAGES[code] || _ERROR_CODE_MESSAGES["unknown"];
    }

    toString(_t: Function): string {
        return _t(this.message);
    }

    /**
     * Unserialize the error object (reverse JSON.stringify).
     */
    static fromJson(values: any) {
        const error = new ErrorMessage();
        error.message = values.message;
        return error;
    }
}
