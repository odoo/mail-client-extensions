import * as React from 'react';
import './Logger.css';
import { ContentType, HttpVerb, sendHttpRequest } from '../../../utils/httpRequest';
import AppContext from '../AppContext';
import api from '../../api';
import { Spinner, SpinnerSize, TooltipHost } from 'office-ui-fabric-react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheck, faEnvelope } from '@fortawesome/free-solid-svg-icons';
import { OdooTheme } from '../../../utils/Themes';
import { _t } from '../../../utils/Translator';
import PostalMime from 'postal-mime';

//total attachments size threshold in megabytes
const SIZE_THRESHOLD_TOTAL = 40;

//single attachment size threshold in megabytes
const SIZE_THRESHOLD_SINGLE_ELEMENT = 10;

type LoggerProps = {
    resId: number;
    model: string;
    tooltipContent: string;
};

type LoggerState = {
    logged: number;
};

class Logger extends React.Component<LoggerProps, LoggerState> {
    constructor(props, context) {
        super(props, context);
        this.state = {
            logged: 0,
        };
    }

    private arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        const chunkSize = 0x8000; // 32KB
        let binary = '';

        for (let i = 0; i < bytes.length; i += chunkSize) {
            binary += String.fromCharCode(...bytes.subarray(i, i + chunkSize));
        }

        return btoa(binary);
    }

    private logRequest = async (event): Promise<any> => {
        event.stopPropagation();

        this.setState({ logged: 1 });
        Office.context.mailbox.item.getAsFileAsync(async (result) => {
            if (!result.value && result.error) {
                this.context.showHttpErrorMessage(result.error);
                this.setState({ logged: 0 });
                return;
            }

            const parser = new PostalMime();
            const email = await parser.parse(atob(result.value));
            const doc = new DOMParser().parseFromString(email.html, 'text/html');

            let node: Element = doc.getElementById('appendonsend');
            // Remove the history and only log the most recent message.
            while (node) {
                const next = node.nextElementSibling;
                node.parentNode.removeChild(node);
                node = next;
            }
            const msgHeader = `<div>${_t('From : %(email)s', {
                email: email.from.address,
            })}</div>`;
            doc.body.insertAdjacentHTML('afterbegin', msgHeader);
            const msgFooter = `<br/><div class="text-muted font-italic">${_t(
                'Logged from',
            )} <a href="https://www.odoo.com/documentation/master/applications/productivity/mail_plugins.html" target="_blank">${_t(
                'Outlook Inbox',
            )}</a></div>`;
            doc.body.insertAdjacentHTML('beforeend', msgFooter);

            const totalSize = email.attachments.reduce((sum, attachment) => sum + attachment.content.byteLength, 0);
            if (totalSize > SIZE_THRESHOLD_TOTAL * 1024 * 1024) {
                const warningMessage = _t(
                    'Warning: Attachments could not be logged in Odoo because their total size' +
                        ' exceeded the allowed maximum.',
                    {
                        size: SIZE_THRESHOLD_TOTAL,
                    },
                );
                doc.body.innerHTML += `<div class="text-danger">${warningMessage}</div>`;
                email.attachments = [];
            }

            const standardAttachments = [];
            const oversizedAttachments = [];
            const inlineAttachments = {};
            email.attachments.forEach((attachment) => {
                if (attachment.disposition === 'inline') {
                    inlineAttachments[attachment.contentId] = attachment;
                } else if (attachment.content.byteLength > SIZE_THRESHOLD_SINGLE_ELEMENT * 1024 * 1024) {
                    oversizedAttachments.push(attachment.filename);
                } else {
                    standardAttachments.push([attachment.filename, this.arrayBufferToBase64(attachment.content)]);
                }
            });

            if (oversizedAttachments.length > 0) {
                const warningMessage = _t(
                    'Warning: Could not fetch the attachments %(attachments)s as their sizes are bigger then the maximum size of %(size)sMB per each attachment.',
                    {
                        attachments: oversizedAttachments.join(', '),
                        size: SIZE_THRESHOLD_SINGLE_ELEMENT,
                    },
                );
                doc.body.innerHTML += `<div class="text-danger">${warningMessage}</div>`;
            }

            const imageElements = Array.from(doc.getElementsByTagName('img')).filter((img) =>
                img.getAttribute('src')?.startsWith('cid:'),
            );
            imageElements.forEach((element) => {
                const attachment = inlineAttachments[`<${element.src.replace(/^cid:/, '')}>`];
                if (attachment?.content.byteLength > SIZE_THRESHOLD_SINGLE_ELEMENT * 1024 * 1024) {
                    element.setAttribute(
                        'alt',
                        _t('Could not display image %(attachmentName)s, size is over limit', {
                            attachmentName: attachment.filename,
                        }),
                    );
                } else if (attachment) {
                    const fileExtension = attachment.filename.split('.')[1];
                    element.setAttribute(
                        'src',
                        `data:image/${fileExtension};base64, ${this.arrayBufferToBase64(attachment.content)}`,
                    );
                }
            });

            const requestJson = {
                res_id: this.props.resId,
                model: this.props.model,
                message: doc.documentElement.outerHTML,
                attachments: standardAttachments,
            };

            const logRequest = sendHttpRequest(
                HttpVerb.POST,
                api.baseURL + api.logSingleMail,
                ContentType.Json,
                this.context.getConnectionToken(),
                requestJson,
                true,
            );
            logRequest.promise
                .then((response) => {
                    const parsed = JSON.parse(response);
                    if (parsed['error']) {
                        this.setState({ logged: 0 });
                        this.context.showHttpErrorMessage();
                        return;
                    } else {
                        this.setState({ logged: 2 });
                    }
                })
                .catch((error) => {
                    this.context.showHttpErrorMessage(error);
                    this.setState({ logged: 0 });
                });
        });
    };

    render() {
        let logContainer = null;
        switch (this.state.logged) {
            case 0:
                logContainer = (
                    <div className="log-container">
                        <TooltipHost content={this.props.tooltipContent}>
                            <div className="odoo-secondary-button log-button" onClick={this.logRequest}>
                                <FontAwesomeIcon icon={faEnvelope} />
                            </div>
                        </TooltipHost>
                    </div>
                );
                break;
            case 1:
                logContainer = (
                    <div className="log-container">
                        <div>
                            <Spinner theme={OdooTheme} size={SpinnerSize.medium} />
                        </div>
                    </div>
                );
                break;
            case 2:
                logContainer = (
                    <div className="log-container">
                        <div className="logged-text">
                            <FontAwesomeIcon icon={faCheck} color={'green'} />
                        </div>
                    </div>
                );
                break;
        }

        return <>{logContainer}</>;
    }
}

Logger.contextType = AppContext;

export default Logger;
