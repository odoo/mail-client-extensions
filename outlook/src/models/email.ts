/**
 * Represent the current email open in the Gmail application.
 */
export class Email {
    subject: string
    timestamp: number
    messageId: string

    emailFrom: string
    contacts: EmailContact[]

    constructor() {
        const userEmail = Office.context.mailbox.userProfile.emailAddress
        const mail = Office.context.mailbox.item

        const values = [
            [mail.from.displayName, mail.from.emailAddress],
            ...mail.to.map((v) => [v.displayName, v.emailAddress]),
            ...mail.cc.map((v) => [v.displayName, v.emailAddress]),
        ]

        this.subject = mail.subject
        this.timestamp = mail.dateTimeCreated.getTime()
        this.messageId = mail.internetMessageId

        this.emailFrom =
            mail.from.displayName != mail.from.emailAddress
                ? `"${mail.from.displayName}" <${mail.from.emailAddress}>`
                : mail.from.emailAddress
        this.contacts = values
            .filter((v) => v[1] !== userEmail)
            .map((v) => new EmailContact(v[0], v[1]))
    }

    /**
     * Return the content of the email.
     */
    async getBody(): Promise<string> {
        return new Promise((resolve) => {
            Office.context.mailbox.item.body.getAsync(
                Office.CoercionType.Html,
                async (result) => {
                    resolve(result.value)
                }
            )
        })
    }

    /**
     * Return the list of attachments in the email if they do not exceed the limit.
     */
    async getAttachments(): Promise<[string, string][] | null> {
        const officeAttachmentDetails = Office.context.mailbox.item.attachments

        const totalSize = officeAttachmentDetails
            .map((officeAttachment) => officeAttachment.size)
            .reduce((partialSum, a) => partialSum + a, 0)

        // total attachments size threshold
        const SIZE_THRESHOLD_TOTAL = 40 * 1024 * 1024

        if (totalSize > SIZE_THRESHOLD_TOTAL) {
            return null
        }

        const promises = officeAttachmentDetails.map((attachment, index) =>
            this.fetchAttachmentContent(attachment, index)
        )

        return Promise.all(promises)
    }

    /**
     * Get the content of the corresponding attachment.
     */
    fetchAttachmentContent(attachment, _index): Promise<[string, string]> {
        return new Promise<any>((resolve) => {
            Office.context.mailbox.item.getAttachmentContentAsync(
                attachment.id,
                (asyncResult) =>
                    resolve([attachment.name, asyncResult.value.content])
            )
        })
    }
}

export class EmailContact {
    name: string
    email: string

    constructor(name: string, email: string) {
        this.name = name
        this.email = email
    }
}
