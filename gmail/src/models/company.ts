import { formatUrl, isTrue, first } from "../utils/format";

export class Company {
    id: number;
    name: string;
    email: string;
    phone: string;

    // Additional Information
    address: string;
    annualRevenue: string;
    companyType: string;
    description: string;
    emails: string;
    employees: number;
    foundedYear: number;
    image: string;
    industry: string;
    mobile: string;
    phones: string;
    tags: string;
    timezone: string;
    timezoneUrl: string;
    twitterFollowers: number;
    twitterBio: string;
    website: string;

    // Social Medias
    crunchbase: string;
    facebook: string;
    linkedin: string;
    twitter: string;

    /**
     * Parse the dictionary returned by IAP.
     */
    static fromIapResponse(values: any): Company {
        const company = new Company();

        company.name = isTrue(values.name);
        company.email = first(values.email);
        company.phone = first(values.phone_numbers);

        company.emails = isTrue(values.email) ? values.email.join("\n") : null;
        company.phones = isTrue(values.phone_numbers) ? values.phone_numbers.join("\n") : null;

        company.image = isTrue(values.logo);
        company.website = formatUrl(values.domain);
        company.description = isTrue(values.description);
        company.address = isTrue(values.location);

        // Social Medias
        company.facebook = isTrue(values.facebook);
        company.twitter = isTrue(values.twitter);
        company.linkedin = isTrue(values.linkedin);
        company.crunchbase = isTrue(values.crunchbase);

        // Additional Information
        company.employees = values.employees || null;
        company.annualRevenue = isTrue(values.estimated_annual_revenue);
        company.industry = isTrue(values.industry);
        company.twitterBio = isTrue(values.twitter_bio);
        company.twitterFollowers = values.twitter_followers || null;
        company.foundedYear = values.founded_year;
        company.timezone = isTrue(values.timezone);
        company.timezoneUrl = isTrue(values.timezone_url);
        company.tags = isTrue(values.tag) ? values.tag.join(", ") : null;
        company.companyType = isTrue(values.company_type);

        return company;
    }

    /**
     * Unserialize the company object (reverse JSON.stringify).
     */
    static fromJson(values: any): Company {
        const company = new Company();

        company.id = values.id;
        company.name = values.name;
        company.email = values.email;
        company.phone = values.phone;

        company.address = values.address;
        company.annualRevenue = values.annualRevenue;
        company.companyType = values.companyType;
        company.description = values.description;
        company.emails = values.emails;
        company.employees = values.employees;
        company.foundedYear = values.foundedYear;
        company.image = values.image;
        company.industry = values.industry;
        company.mobile = values.mobile;
        company.phones = values.phones;
        company.tags = values.tags;
        company.timezone = values.timezone;
        company.timezoneUrl = values.timezoneUrl;
        company.twitterBio = values.twitterBio;
        company.twitterFollowers = values.twitterFollowers;
        company.website = values.website;

        company.crunchbase = values.crunchbase;
        company.facebook = values.facebook;
        company.twitter = values.twitter;
        company.linkedin = values.linkedin;

        return company;
    }

    /**
     * Parse the dictionary returned by an Odoo database.
     */
    static fromOdooResponse(values: any): Company {
        if (!values.id || values.id < 0) {
            return null;
        }

        const iapInfo = values.additionalInfo || {};

        const company = this.fromIapResponse(iapInfo);

        // Overwrite IAP information with the Odoo client database information
        company.id = values.id;
        company.name = values.name;
        company.email = values.email;
        company.phone = values.phone;

        company.mobile = values.mobile;
        company.website = values.website;
        company.image = values.image ? "data:image/png;base64," + values.image : null;

        if (values.address) {
            company.address = "";

            if (isTrue(values.address.street)) {
                company.address += values.address.street + ", ";
            }
            if (isTrue(values.address.zip)) {
                company.address += values.address.zip + " ";
            }
            if (isTrue(values.address.city)) {
                company.address += values.address.city + " ";
            }
            if (isTrue(values.address.country)) {
                company.address += values.address.country;
            }
        }
        return company;
    }
}
