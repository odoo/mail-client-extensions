import PostalMime from 'postal-mime'

/**
 * Represent the current email open in the Outlook application.
 */
export class Email {
    subject: string
    timestamp: number
    messageId: string

    emailFrom: string
    emailTo: string
    emailCC: string
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

        /**
         * Parse the email address detail from the Office library and convert them to string.
         */
        const mailToString = (mail: Office.EmailAddressDetails): string => {
            return mail.displayName != mail.emailAddress
                ? `"${mail.displayName}" <${mail.emailAddress}>`
                : mail.emailAddress
        }

        this.emailFrom = mailToString(mail.from)
        this.emailTo = mail.to.map(mailToString).join(', ')
        this.emailCC = mail.cc.map(mailToString).join(', ')
        this.contacts = values
            .filter((v) => v[1] !== userEmail)
            .map((v) => new EmailContact(v[0], v[1]))
    }

    /**
     * Return the content of the email.
     */
    async getBody(): Promise<string> {
        let body: string = await new Promise((resolve) => {
            Office.context.mailbox.item.body.getAsync(
                Office.CoercionType.Html,
                async (result) => {
                    resolve(result.value)
                }
            )
        })

        // add inline images
        const emailB64: string = await new Promise((resolve) => {
            Office.context.mailbox.item.getAsFileAsync((result) => {
                resolve(result.value)
            })
        })
        const email = await PostalMime.parse(atob(emailB64))
        const toBase64 = (buffer: ArrayBuffer) => {
            let binary = ''
            const bytes = new Uint8Array(buffer)
            for (let i = 0; i < bytes.byteLength; i++) {
                binary += String.fromCharCode(bytes[i])
            }
            return btoa(binary)
        }

        for (const attachment of email.attachments) {
            if (!attachment.contentId || attachment.disposition !== 'inline') {
                continue
            }
            const contentId = attachment.contentId
                .replace('<', '')
                .replace('>', '')
            const content = attachment.content as ArrayBuffer
            const base64Data = `data:${attachment.mimeType};base64,${toBase64(content)}`
            body = body.replace(`cid:${contentId}`, base64Data)
        }

        return body
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

        const promises = officeAttachmentDetails
            .filter((attachment) => !attachment.isInline)
            .map((attachment) => this.fetchAttachmentContent(attachment))

        return Promise.all(promises)
    }

    /**
     * Get the content of the corresponding attachment.
     */
    fetchAttachmentContent(
        attachment: Office.AttachmentDetails
    ): Promise<[string, string]> {
        return new Promise((resolve) => {
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
