import * as React from 'react';
import AppContext from '../../../AppContext';
import Partner from '../../../../../classes/Partner';
import './ContactListItem.css';
import Logger from '../../../Log/Logger';
import { faEnvelope, faPhone } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { TooltipHost, TooltipOverflowMode } from 'office-ui-fabric-react';
import { _t } from '../../../../../utils/Translator';

const defaultCompanyImageSrc = 'assets/company_image.png';

type CustomContactListItemProps = {
    partner: Partner;
    canCreatePartner: boolean;
    onItemClick?: (partner: Partner) => void;
};

class ContactListItem extends React.Component<CustomContactListItemProps, {}> {
    constructor(props, context) {
        super(props, context);
        this.state = {};
    }

    private getIconOrInitials = () => {
        const partnerImage = this.props.partner.image;
        if (partnerImage) {
            return <img className="icon" src={`data:image;base64, ${partnerImage}`} />;
        } else if (this.props.partner.isCompany) {
            return <img className="icon" src={defaultCompanyImageSrc} />;
        }
        return <div data-initials={this.props.partner.getInitials()} />;
    };

    private onPartnerClick = () => {
        this.props.onItemClick(this.props.partner);
    };

    render() {
        const logButton = this.props.partner.isAddedToDatabase() && this.props.partner.canWriteOnPartner && (
            <Logger resId={this.props.partner.id} model="res.partner" tooltipContent={_t('Log Email Into Contact')} />
        );

        const { name, email, title: jobTitle, phone } = this.props.partner;
        const contactName = jobTitle ? name + ', ' + jobTitle : name;

        const emailDiv = email && (
            <div className="contact-email">
                <FontAwesomeIcon icon={faEnvelope} className="contact-info-icon fa-fw" />
                <div className="text-truncate">
                    <TooltipHost content={email} overflowMode={TooltipOverflowMode.Parent}>
                        {email}
                    </TooltipHost>
                </div>
            </div>
        );

        const phoneDiv = phone && (
            <div className="contact-phone">
                <FontAwesomeIcon icon={faPhone} className="contact-info-icon fa-fw" />
                <a className="link-like-button" href={`tel:${phone}`}>
                    {phone}
                </a>
            </div>
        );

        return (
            <div className={`contact-container ${this.props.onItemClick && 'clickable'}`} onClick={this.onPartnerClick}>
                <div className="contact-card">
                    {this.getIconOrInitials()}
                    <div className="contact-info">
                        <div className="contact-name">{contactName}</div>
                        {emailDiv}
                        {phoneDiv}
                    </div>
                </div>
                {logButton}
            </div>
        );
    }
}
ContactListItem.contextType = AppContext;
export default ContactListItem;
