import * as React from 'react';
import './ProfileCard.css';
import { faEnvelope, faPhone } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { TooltipHost, TooltipOverflowMode } from 'office-ui-fabric-react';
import AppContext from '../AppContext';

const defaultCompanyImageSrc = 'assets/company_image.png';

export type ProfileCardProps = {
    domain: string;
    icon: string;
    initials: string;
    name: string;
    email: string;
    job: string;
    phone: string;
    description: string;
    twitter: string;
    facebook: string;
    crunchbase: string;
    linkedin: string;
    onClick?: () => void;
    isBig?: boolean; //used for email overflow, TODO change maybe by obtaining the width dynamically
    isCompany: boolean;
    parentIsCompany?: boolean;
};

export class ProfileCard extends React.Component<ProfileCardProps, {}> {
    constructor(props, context) {
        super(props, context);
        this.state = {};
    }

    private addDefaultSrc(ev) {
        ev.target.src = defaultCompanyImageSrc;
    }

    private getIconOrInitials = () => {
        if (this.props.parentIsCompany) {
            return null;
        }

        let iconOrInitials = <img className="icon" src={this.props.icon} onError={this.addDefaultSrc} />;

        if (!this.props.icon) {
            if (this.props.isCompany) {
                iconOrInitials = <img className="icon" src={defaultCompanyImageSrc} />;
            } else {
                iconOrInitials = <div data-initials={this.props.initials}></div>;
            }
        } else {
            if (this.props.domain) {
                iconOrInitials = (
                    <a href={this.props.domain} target="_blank" rel="noreferrer noopener">
                        {iconOrInitials}
                    </a>
                );
            }
        }

        return iconOrInitials;
    };

    private getTextWidth = (text, font) => {
        // re-use canvas object for better performance
        var canvas = document.createElement('canvas');
        var context = canvas.getContext('2d');
        context.font = font;
        var metrics = context.measureText(text);
        return metrics.width;
    };

    render() {
        const { name, email, job, phone, description, twitter, facebook, linkedin, crunchbase } = this.props;
        const iconOrInitials = this.getIconOrInitials();

        let nameJob = job ? name + ', ' + job : name;

        const nameSize = this.getTextWidth(nameJob, 'bold 16px Arial');
        const nameSizeCutoff = 150;

        // If the size of the text is smaller than the cutoff and the parent is not a company, the social links should be on the right of the name.
        const social = (
            <div
                className={`social-links ${nameSize < nameSizeCutoff && !this.props.parentIsCompany ? 'right' : null}`}>
                {twitter ? (
                    <a href={'https://twitter.com/' + twitter} target="_blank" rel="noreferrer noopener">
                        <img src="assets/social/twitter.ico" />
                    </a>
                ) : null}
                {facebook ? (
                    <a href={'https://facebook.com/' + twitter} target="_blank" rel="noreferrer noopener">
                        <img src="assets/social/facebook.ico" />
                    </a>
                ) : null}
                {linkedin ? (
                    <a href={'https://linkedin.com/' + linkedin} target="_blank" rel="noreferrer noopener">
                        <img src="assets/social/linkedin.ico" />
                    </a>
                ) : null}
                {crunchbase ? (
                    <a href={'https://crunchbase.com/' + crunchbase} target="_blank" rel="noreferrer noopener">
                        <img src="assets/social/crunchbase.ico" />
                    </a>
                ) : null}
            </div>
        );

        let emailDiv = null;

        //TODO, can we calculate width dynamically?
        let maxEmailWidth = this.props.isBig ? 180 : 120;

        const nameDiv = !this.props.parentIsCompany ? <div className="name">{nameJob}</div> : null;

        if (email && !this.props.parentIsCompany) {
            emailDiv = (
                <div className="profile-card-email" style={{ display: 'flex', flexDirection: 'row' }}>
                    <div>
                        <FontAwesomeIcon
                            style={{ marginRight: '4px' }}
                            icon={faEnvelope}
                            color="darkgrey"
                            className="fa-fw"
                        />
                    </div>
                    <div
                        style={{
                            overflow: 'hidden',
                            whiteSpace: 'nowrap',
                            textOverflow: 'ellipsis',
                            maxWidth: maxEmailWidth + 'px',
                        }}>
                        <TooltipHost content={email} overflowMode={TooltipOverflowMode.Parent}>
                            {email}
                        </TooltipHost>
                    </div>
                </div>
            );
        }

        let phoneDiv = null;
        if (phone && !this.props.parentIsCompany) {
            phoneDiv = (
                <div className="phone">
                    <div>
                        <FontAwesomeIcon
                            style={{ marginRight: '4px' }}
                            icon={faPhone}
                            color="darkgrey"
                            className="fa-fw"
                        />
                    </div>
                    <div>
                        <a className="link-like-button" href={`tel:${phone}`}>
                            {phone}
                        </a>
                    </div>
                </div>
            );
        }

        let descriptionDiv = null;
        if (description && description !== '') {
            descriptionDiv = <div style={{ padding: '0 8px 0 8px' }}>{description}</div>;
        }

        let profileCardClassName = 'profile-card';
        if (this.props.onClick && !this.props.parentIsCompany) {
            profileCardClassName += ' clickable';
        } else {
            if (this.props.parentIsCompany) {
                profileCardClassName += ' with-padding';
            }
        }

        return (
            <>
                <div>
                    <div className={profileCardClassName} onClick={this.props.onClick}>
                        {iconOrInitials}
                        <div>
                            {nameDiv}
                            {emailDiv}
                            {phoneDiv}
                        </div>
                        {nameSize < nameSizeCutoff || this.props.parentIsCompany ? social : null}
                    </div>
                    <div className="profile-card">
                        {nameSize > nameSizeCutoff && !this.props.parentIsCompany ? social : null}
                    </div>
                </div>
                {descriptionDiv}
            </>
        );
    }
}

ProfileCard.contextType = AppContext;
