import * as React from "react";
import './ProfileCard.css';

export type ProfileCardProps = {
    icon: string;
    initials: string;
    name: string;
    job: string;
    phone: string;
    description: string;
    twitter: string;
    facebook: string;
    crunchbase: string;
    linkedin: string;
};
type ProfileCardState = {};

export class ProfileCard extends React.Component<ProfileCardProps, ProfileCardState> {
    constructor(props, context) {
        super(props, context);
        this.state = {};
    }

    getTextWidth = (text, font) => {
        // re-use canvas object for better performance
        var canvas = document.createElement("canvas");
        var context = canvas.getContext("2d");
        context.font = font;
        var metrics = context.measureText(text);
        return metrics.width;
    }

    render() {
        const {icon, name, initials, job, phone, description, twitter, facebook, linkedin, crunchbase} = this.props;
        let iconOrInitials = <img className='icon' src={icon}/>;
        if (!icon) {
            iconOrInitials = <div data-initials={initials}></div>
        }
        const nameSize = this.getTextWidth(name, 'bold 20px Arial')
        const nameSizeCutoff = 150;

        // If the size of the text is smaller than the cutoff, the social links should be on the right of the name.
        const social = <div className={`social-links ${nameSize < nameSizeCutoff ? 'right' : null}`}>
            {twitter ? <a href={'https://twitter.com/' + twitter} target='_blank' rel="noreferrer noopener"><img src='../../../../assets/social/twitter.ico'/></a> : null}
            {facebook ? <a href={'https://facebook.com/' + twitter} target='_blank' rel="noreferrer noopener"><img src='../../../../assets/social/facebook.ico'/></a> : null}
            {linkedin ? <a href={'https://linkedin.com/' + linkedin} target='_blank' rel="noreferrer noopener"><img src='../../../../assets/social/linkedin.ico'/></a> : null}
            {crunchbase ? <a href={'https://crunchbase.com/' + crunchbase} target='_blank' rel="noreferrer noopener"><img src='../../../../assets/social/crunchbase.ico'/></a> : null}
        </div>

        return (
            <>
                <div className='profile-card'>
                    {iconOrInitials}
                    <div>
                        <div className='name'>{name}</div>
                        <div className='job'>{job}</div>
                        <div className='phone'><a className="link-like-button" href={`tel:${phone}`}>{phone}</a></div>
                    </div>
                    {nameSize < nameSizeCutoff ? social : null}
                </div>
                <div className='profile-card'>{nameSize > nameSizeCutoff ? social : null}</div>
                <div className='profile-card description'>{description}</div>
            </>
        );
    }
}

