import * as React from "react";
import './ProfileCard.css';
import {faEnvelope, faPhone} from "@fortawesome/free-solid-svg-icons";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {TooltipHost} from "office-ui-fabric-react";
import AppContext from "../AppContext";

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
};

export class ProfileCard extends React.Component<ProfileCardProps, {}> {
    constructor(props, context) {
        super(props, context);
        this.state = {};
    }

    private getTextWidth = (text, font) => {
        // re-use canvas object for better performance
        var canvas = document.createElement("canvas");
        var context = canvas.getContext("2d");
        context.font = font;
        var metrics = context.measureText(text);
        return metrics.width;
    }

    render() {
        const {domain, icon, name, email, initials, job, phone, description, twitter, facebook, linkedin, crunchbase} = this.props;

        let iconOrInitials = <img className='icon' src={icon}/>;
        if (!icon) {
            iconOrInitials = <div data-initials={initials}></div>
        }
        
        if (domain) {
            iconOrInitials = <a href={domain} target='_blank' rel="noreferrer noopener">{iconOrInitials}</a>
        }

        let nameJob = job? name+', '+job : name;

        const nameSize = this.getTextWidth(nameJob, 'bold 16px Arial')
        const nameSizeCutoff = 150;

        // If the size of the text is smaller than the cutoff, the social links should be on the right of the name.
        const social = <div className={`social-links ${nameSize < nameSizeCutoff ? 'right' : null}`}>
            {twitter ? <a href={'https://twitter.com/' + twitter} target='_blank' rel="noreferrer noopener"><img src='assets/social/twitter.ico'/></a> : null}
            {facebook ? <a href={'https://facebook.com/' + twitter} target='_blank' rel="noreferrer noopener"><img src='assets/social/facebook.ico'/></a> : null}
            {linkedin ? <a href={'https://linkedin.com/' + linkedin} target='_blank' rel="noreferrer noopener"><img src='assets/social/linkedin.ico'/></a> : null}
            {crunchbase ? <a href={'https://crunchbase.com/' + crunchbase} target='_blank' rel="noreferrer noopener"><img src='assets/social/crunchbase.ico'/></a> : null}
        </div>

        let emailDiv = null;

        //TODO, can we calculate width dynamically?
        let maxEmailWidth = (this.props.isBig) ? 180 : 120;

        if (email)
        {
            let emailTextContainer = null;
            let emailSize = this.getTextWidth(email, "normal 14px Arial");
            if (emailSize > maxEmailWidth)
            {
                emailTextContainer = (
                    <TooltipHost content={email}>
                        {email}
                    </TooltipHost>
                );
            }
            else
            {
                emailTextContainer = (
                    <>
                        {email}
                    </>
                );
            }
            emailDiv = (
                    <div className='profile-card-email' style={{display: "flex", flexDirection: "row"}}>
                        <div>
                            <FontAwesomeIcon style = {{marginRight: '4px'}} icon={faEnvelope} color='darkgrey' className="fa-fw"/>
                        </div>
                        <div style={{overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis", maxWidth: maxEmailWidth + "px"}}>
                            {emailTextContainer}
                        </div>
                    </div>
            );
        }

        let phoneDiv = null;
        if (phone)
        {
            phoneDiv = (
                <div className='phone'>
                    <div>
                        <FontAwesomeIcon style = {{marginRight: '4px'}} icon={faPhone} color='darkgrey' className="fa-fw"/>
                    </div>
                    <div>
                        <a className="link-like-button" href={`tel:${phone}`}>{phone}</a>
                    </div>
                </div>
            );
        }

        let descriptionDiv = null;
        if (description && description !== '')
        {
            descriptionDiv =
                (
                    <div style={{padding: "0 8px 0 8px"}}>
                        {description}
                    </div>
                );
        }

        let profileCardClassName = 'profile-card';
        if (this.props.onClick)
        {
            profileCardClassName += ' clickable';
        }

        return (
            <>
                <div>
                    <div className={profileCardClassName} onClick={this.props.onClick}>
                        {iconOrInitials}
                        <div>
                            <div className='name'>{nameJob}</div>
                            {emailDiv}
                            {phoneDiv}
                        </div>
                        {nameSize < nameSizeCutoff ? social : null}
                    </div>
                    <div className='profile-card'>{nameSize > nameSizeCutoff ? social : null}</div>
                </div>
                {descriptionDiv}
            </>
        );
    }
}

ProfileCard.contextType = AppContext;

