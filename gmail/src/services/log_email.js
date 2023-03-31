/**
 * Format the email body before sending it to Odoo.
 * Add error message at the end of the email, fix some CSS issues,...
 */
function _formatEmailBody(email, error) {
    var header = "<span>".concat((0, _t)("Subject:"), " ").concat((0, escapeHtml)(email.subject), "</span><br/>");
    header += "<span>".concat((0, _t)("From:"), " ").concat((0, escapeHtml)(email.contactEmail), "</span><br/><br/>");
    var body = header.concat(email.body);
    if (error.code === "attachments_size_exceeded") {
        body += "<br/><i>".concat(
            (0, _t)("Attachments could not be logged in Odoo because their total size exceeded the allowed maximum."),
            "</i>",
        );
    }
    // Make the "attachment" links bigger, otherwise we need to scroll to fully see them
    // Can not add a <style/> tag because they are sanitized by Odoo
    body = body.replace(
        /class=\"gmail_chip gmail_drive_chip" style=\"/g,
        'class="gmail_chip gmail_drive_chip" style=" min-height: 32px;',
    );
    body += "<br/><br/>".concat((0, _t)("Logged from"), "<b> ").concat((0, _t)("Gmail Inbox"), "</b>");
    return body;
}
/**
 * Log the given email body in the chatter of the given record.
 */
function logEmail(recordId, recordModel, email) {
    var accessToken = State.accessToken;
    var _a = email.getAttachments(),
        attachments = _a[0],
        error = _a[1];
    var body = _formatEmailBody(email, error);
    var url = State.odooServerUrl + URLS.LOG_EMAIL;
    var response = (0, postJsonRpc)(
        url,
        { message: body, res_id: recordId, model: recordModel, attachments: attachments },
        { Authorization: "Bearer " + accessToken },
    );
    if (!response) {
        error.setError("unknown");
    }
    return error;
}
