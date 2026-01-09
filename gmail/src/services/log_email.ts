import { URLS } from "../consts";
import { Email } from "../models/email";
import { ErrorMessage } from "../models/error_message";
import { User } from "../models/user";
import { postJsonRpc } from "../utils/http";

/**
 * Format the email body before sending it to Odoo.
 * Add error message at the end of the email, fix some CSS issues,...
 */
function _formatEmailBody(_t: Function, body: string, error: ErrorMessage): string {
    if (error.code === "attachments_size_exceeded") {
        body += `<br/><i>${_t(
            "Attachments could not be logged in Odoo because their total size exceeded the allowed maximum.",
        )}</i>`;
    }

    // Make the "attachment" links bigger, otherwise we need to scroll to fully see them
    // Can not add a <style/> tag because they are sanitized by Odoo
    body = body.replace(
        /class=\"gmail_chip gmail_drive_chip" style=\"/g,
        'class="gmail_chip gmail_drive_chip" style=" min-height: 32px;',
    );
    return body;
}

/**
 * Log the given email body in the chatter of the given record.
 */
export async function logEmail(
    _t: Function,
    user: User,
    recordId: number,
    recordModel: string,
    email: Email,
): Promise<ErrorMessage> {
    const [rawBody, timestamp, [attachments, error]] = await email.getBodyAndAttachments();
    const body = _formatEmailBody(_t, rawBody, error);

    const response = await postJsonRpc(
        user.odooUrl + URLS.LOG_EMAIL,
        {
            body,
            res_id: recordId,
            model: recordModel,
            attachments: attachments,
            email_from: email.emailFrom,
            email_to: email.emailTo,
            email_cc: email.emailCC,
            subject: email.subject,
            timestamp: timestamp,
            application_name: _t("Odoo for Gmail"),
        },
        { Authorization: "Bearer " + user.odooToken },
    );

    if (!response) {
        return new ErrorMessage("unknown");
    }

    return error;
}
