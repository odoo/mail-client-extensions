/**
 * Represent the current email open in the Gmail application.
 */
var Email = /** @class */ (function () {
    function Email(messageId, accessToken) {
        var _a;
        if (messageId === void 0) {
            messageId = null;
        }
        if (accessToken === void 0) {
            accessToken = null;
        }
        if (messageId) {
            var userEmail = Session.getEffectiveUser().getEmail().toLowerCase();
            this.accessToken = accessToken;
            this.messageId = messageId;
            var message = GmailApp.getMessageById(this.messageId);
            this.subject = message.getSubject();
            var fromHeaders = message.getFrom();
            var sent = fromHeaders.toLowerCase().indexOf(userEmail) >= 0;
            this.contactFullEmail = sent ? message.getTo() : message.getFrom();
            (_a = this._emailSplitTuple(this.contactFullEmail)),
                (this.contactName = _a[0]),
                (this.contactEmail = _a[1]);
        }
    }
    Object.defineProperty(Email.prototype, "body", {
        /**
         * Ask the email body only if the user asked for it (e.g. asked to log the email).
         */
        get: function () {
            GmailApp.setCurrentMessageAccessToken(this.accessToken);
            var message = GmailApp.getMessageById(this.messageId);
            return message.getBody();
        },
        enumerable: false,
        configurable: true,
    });
    /**
     * Parse a full FROM header and return the name part and the email part.
     *
     * E.G.
     *     "BOB" <bob@example.com> => ["BOB", "bob@example.com"]
     *     bob@example.com         => ["bob@example.com", "bob@example.com"]
     *
     */
    Email.prototype._emailSplitTuple = function (fullEmail) {
        var match = fullEmail.match(/(.*)<(.*)>/);
        fullEmail = fullEmail.replace("<", "").replace(">", "");
        if (!match) {
            return [fullEmail, fullEmail];
        }
        var _ = match[0],
            name = match[1],
            email = match[2];
        if (!name || !email) {
            return [fullEmail, fullEmail];
        }
        var cleanedName = name.replace(/\"/g, "").trim();
        if (!cleanedName || !cleanedName.length) {
            return [fullEmail, fullEmail];
        }
        return [cleanedName, email];
    };
    /**
     * Unserialize the email object (reverse JSON.stringify).
     */
    Email.fromJson = function (values) {
        var email = new Email();
        email.accessToken = values.accessToken;
        email.messageId = values.messageId;
        email.subject = values.subject;
        email.contactEmail = values.contactEmail;
        email.contactFullEmail = values.contactFullEmail;
        email.contactName = values.contactName;
        return email;
    };
    /**
     * Return the list of the attachments in the email.
     * Done in a getter and not as a property because this object is serialized and
     * given to the event handler.
     *
     * Returns:
     *     - Null and "attachments_size_exceeded" error, if the total attachment size limit
     *       is exceeded so we do not keep big files in memory.
     *     - If no attachment, return an empty array and an empty error message.
     *     - Otherwise, the list of attachments base 64 encoded and an empty error message
     */
    Email.prototype.getAttachments = function () {
        GmailApp.setCurrentMessageAccessToken(this.accessToken);
        var message = GmailApp.getMessageById(this.messageId);
        var gmailAttachments = message.getAttachments();
        var attachments = [];
        // The size limit of the POST request are 50 MB
        // So we limit the total attachment size to 40 MB
        var MAXIMUM_ATTACHMENTS_SIZE = 40 * 1024 * 1024;
        var totalAttachmentsSize = 0;
        for (var _i = 0, gmailAttachments_1 = gmailAttachments; _i < gmailAttachments_1.length; _i++) {
            var gmailAttachment = gmailAttachments_1[_i];
            var bytesSize = gmailAttachment.getSize();
            totalAttachmentsSize += bytesSize;
            if (totalAttachmentsSize > MAXIMUM_ATTACHMENTS_SIZE) {
                return [null, new ErrorMessage("attachments_size_exceeded")];
            }
            var name = gmailAttachment.getName();
            var content = Utilities.base64Encode(gmailAttachment.getBytes());
            attachments.push([name, content]);
        }
        return [attachments, new ErrorMessage(null)];
    };
    return Email;
})();
