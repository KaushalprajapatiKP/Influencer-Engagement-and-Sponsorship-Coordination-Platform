Project Statement: Influencer Engagement & Sponsorship Coordination Platform - V2
The Influencer Engagement & Sponsorship Coordination Platform is designed to create a seamless connection between sponsors and influencers, enabling sponsors to effectively promote their products and services while providing influencers with opportunities for monetary compensation.

Frameworks and Technologies
The platform utilizes a robust set of technologies to ensure a high-performing, user-friendly application:

Vue CLI: For developing a responsive and interactive front-end interface.
Bootstrap: For modern and clean styling of the application.
Flask-CORS: To manage cross-origin requests and ensure smooth communication between the front-end and back-end.
Flask-RESTful: To build a RESTful API for effective client-server communication.
Jinja2: For dynamic HTML template rendering, especially in email content.
SQLite: For lightweight and reliable data storage.
Flask-SQLAlchemy: As an Object-Relational Mapping (ORM) tool for simplifying database interactions.
Flask-Celery: To manage asynchronous background jobs, improving task processing efficiency.
Redis: For in-memory caching of API responses and as a message broker for Celery.
Flask-Caching: To enhance performance through cached API outputs.
Technology Versions
Flask==2.2.3
Flask-SQLAlchemy==3.0.3
Flask-Mail==0.10.0
Flask-RESTful==0.3.10
Flask-Security-Too==5.1.2
Flask-Login==0.6.2
Flask-WTF==1.1.1
Flask-CORS==3.0.10
Celery==5.4.0
redis==5.0.1
User Roles
The platform will support three primary user roles:

Admin (Root Access):

Monitor all users and campaigns.
View comprehensive statistics.
Flag inappropriate campaigns/users.
Sponsors (Companies/Individuals Advertising):

Create and manage campaigns.
Search for influencers and send ad requests.
Track multiple campaigns.
Each Sponsor profile includes:
Company/Individual Name
Industry
Budget
Influencers (Individuals with Social Media Following):

Receive, accept, reject, and negotiate ad requests.
Search for ongoing public campaigns by category and budget.
Update publicly visible profiles.
Each Influencer profile includes:
Name
Category
Niche
Reach (calculated by followers/activity)
Key Terminologies
Ad Request: A contract between a campaign and an influencer, detailing advertisement requirements and payment.

Fields:
campaign_id: Foreign Key to Campaign table
influencer_id: Foreign Key to Influencer table
messages
requirements
payment_amount
status (Pending, Accepted, Rejected)
Campaign: A container for ad requests aimed at achieving specific advertising goals.

Fields:
name
description
start_date
end_date
budget
visibility (public/private)
goals
Application Wireframe


Note: The wireframe is meant to guide the application flow and does not need to be strictly replicated in the UI.

Core Functionalities
User Authentication (RBAC):

Implement a secure login/register form with fields for username and password.
Use Flask Security or JWT for role-based access control.
Admin Dashboard:

Auto-add the admin upon database creation.
Approve new sponsor sign-ups.
Display statistics on active users, campaigns, ad requests, flagged users, etc.
Campaign Management for Sponsors:

Create, update, and delete campaigns.
Categorize campaigns into various niches.
Ad Request Management for Sponsors:

Create, edit, and delete ad requests based on campaign goals.
Search Functionality:

Sponsors can search for influencers based on specific criteria.
Influencers can search for public campaigns.
Ad Request Actions for Influencers:

View and manage ad requests from campaigns.
Accept, reject, or negotiate ad requests.
Backend Jobs:

Daily Reminders: Send reminders to influencers via Google Chat, SMS, or email.
Monthly Activity Reports: Generate and email reports to sponsors detailing campaign performance.
CSV Export: Allow sponsors to download campaign details in CSV format.
Performance and Caching:

Implement caching to optimize performance.
Use Redis for API response caching.
Recommended Functionalities
Dynamic PDF reports for monthly activity.
Integration with external libraries for charts (e.g., ChartJS).
Responsive UI for mobile and desktop.
Validations on form fields (HTML5 and JavaScript).
Optional Functionalities
Enhance UI with CSS or Bootstrap.
Implement a robust login system.
Create a dummy payment portal for ad requests.
Additional features deemed appropriate for the application.
Key Features Overview
User Roles and Authentication: Support for Admin, Sponsor, and Influencer roles with secure login.
Admin Dashboard: Comprehensive monitoring and approval system.
Campaign Management: Tools for sponsors to create and manage campaigns efficiently.
Ad Request Management: Features to create and track ad requests.
Influencer Interaction: Notifications and negotiation capabilities for influencers.
Search Functionality: Enhanced search for sponsors and influencers.
Backend Jobs: Automated reminders, reports, and CSV exports.
Performance and Caching: Caching strategies to improve API performance.
User-Friendly Interface: Responsive design with Bootstrap for better user experience.
Reporting and Analytics: Generate actionable reports for users.

Database Schema

1. User
   - id: Integer, Primary Key, Not Null
   - name: String, Not Null
   - email: String(255), Unique, Not Null
   - password: String(255), Not Null
   - last_login_at: DateTime
   - fs_uniquifier: String(255), Unique, Not Null
   - active: Boolean
   - roles: Many-to-Many relationship with Role through UserRoles

2. Role
   - id: Integer, Primary Key
   - name: String(80), Unique
   - description: String(255)

3. UserRoles (Associative Table for User and Role)
   - id: Integer, Primary Key, Not Null
   - role_id: Integer, Foreign Key (Role.id), Not Null, On Delete CASCADE
   - user_id: Integer, Foreign Key (User.id), Not Null, On Delete CASCADE

4. Admin
   - id: Integer, Primary Key
   - email: String(80), Unique, Not Null
   - password: String(80), Not Null
   - name: String(80), Nullable
   - user_id: Integer, Foreign Key (User.id), Not Null, On Delete CASCADE
   - user: One-to-Many relationship with User

5. Sponsors
   - id: Integer, Primary Key
   - name: String(80), Unique, Not Null
   - email: String(80), Unique, Not Null
   - company_name: String(80), Unique, Not Null
   - industry_name: String(80), Nullable
   - password: String(80), Not Null
   - budget: Integer, Nullable
   - user_id: Integer, Foreign Key (User.id), Not Null, On Delete CASCADE
   - user: One-to-Many relationship with User
   - campaigns: One-to-Many relationship with Campaign

6. Pending_Sponsors
   - id: Integer, Primary Key
   - name: String(80), Unique, Not Null
   - email: String(80), Unique, Not Null
   - company_name: String(80), Unique, Not Null
   - industry_name: String(80), Nullable
   - password: String(80), Not Null
   - budget: Integer, Nullable

7. Influencers
   - id: Integer, Primary Key
   - name: String(80), Unique, Not Null
   - email: String(80), Unique, Not Null
   - password: String(80), Not Null
   - category: String(80), Nullable
   - niche: String(80), Not Null
   - followers: Integer, Not Null, Default=0
   - user_id: Integer, Foreign Key (User.id), Not Null, On Delete CASCADE
   - user: One-to-Many relationship with User

8. Campaign
   - id: Integer, Primary Key
   - name: String(80)
   - description: String(1080)
   - start_date: Date, Default=Current Date
   - end_date: Date
   - budget: Integer, Default=0
   - budget_used: Integer, Default=0
   - visibility: Boolean, Default=False
   - goals: String(1080)
   - flagged: Boolean, Default=False
   - sponsor_id: Integer, Foreign Key (Sponsors.id), Not Null, On Delete CASCADE

9. AdRequests
   - id: Integer, Primary Key
   - campaign_id: Integer, Foreign Key (Campaign.id)
   - influencer_id: Integer, Foreign Key (Influencers.id)
   - status: String(24)
   - messages: String(540)
   - requirements: String(540)
   - payment_amount: Integer
   - campaign: One-to-Many relationship with Campaign
   - influencer: One-to-Many relationship with Influencers

10. CampaignReview
    - id: Integer, Primary Key
    - influencer_id: Integer, Foreign Key (Influencers.id), Not Null
    - campaign_id: Integer, Foreign Key (Campaign.id), Not Null
    - rating: Integer, Not Null
    - review_text: Text, Nullable
    - created_at: DateTime, Default=Current DateTime
    - influencer: One-to-Many relationship with Influencers
    - campaign: One-to-Many relationship with Campaign

11. InfluencerReview
    - id: Integer, Primary Key
    - sponsor_id: Integer, Foreign Key (Sponsors.id), Not Null
    - influencer_id: Integer, Foreign Key (Influencers.id), Not Null
    - rating: Integer, Not Null
    - review_text: Text, Nullable
    - created_at: DateTime, Default=Current DateTime
    - sponsor: One-to-Many relationship with Sponsors
    - influencer: One-to-Many relationship with Influencers


This comprehensive project statement outlines the functionalities and framework for the Influencer Engagement & Sponsorship Coordination Platform - V2, detailing the roles, core functionalities, and the underlying technology stack that supports this dynamic platform.




