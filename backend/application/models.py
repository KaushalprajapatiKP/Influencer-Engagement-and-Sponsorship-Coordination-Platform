from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    last_login_at = db.Column(db.DateTime())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary='roles_users', backref=db.backref('users', lazy='dynamic'))


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    
class UserRoles(db.Model):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    role_id = db.Column(db.Integer(), db.ForeignKey("role.id", ondelete='CASCADE'), nullable= False)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id", ondelete='CASCADE'), nullable= False)

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    name = db.Column(db.String(80), nullable=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('admins', lazy='dynamic'))

class Sponsors(db.Model):
    __tablename__ ='sponsors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    company_name = db.Column(db.String(80), unique=True, nullable=False)
    industry_name = db.Column(db.String(80), unique=False, nullable=True)
    password = db.Column(db.String(80), nullable=False, unique=False)
    budget = db.Column(db.Integer, unique=False, nullable=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('sponsor', lazy='dynamic'))
    campaigns = db.relationship('Campaign', backref='sponsor', lazy=True)

class Pending_Sponsors(db.Model):
    __tablename__ ='pending_sponsors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    company_name = db.Column(db.String(80), unique=True, nullable=False)
    industry_name = db.Column(db.String(80), unique=False, nullable=True)
    password = db.Column(db.String(80), nullable=False, unique=False)
    budget = db.Column(db.Integer, unique=False, nullable=True)
    

class Influencers(db.Model):
    __tablename__ = 'influencers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False, unique=False)
    category = db.Column(db.String(80), unique=False, nullable=True)
    niche = db.Column(db.String(80), unique=False, nullable=False)
    followers = db.Column(db.Integer, nullable=False, default=0)
    # activities = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('influencer', lazy='dynamic'))

class Campaign(db.Model):
    __tablename__ = 'campaign'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.String(1080))
    start_date = db.Column(db.Date, default=datetime.now)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Integer, default=0)
    budget_used = db.Column(db.Integer, default=0)
    visibility = db.Column(db.Boolean, default=False)
    goals = db.Column(db.String(1080))
    flagged = db.Column(db.Boolean, default=False)
    sponsor_id = db.Column(db.Integer(), db.ForeignKey('sponsors.id', ondelete='CASCADE'), nullable=False)


class AdRequests(db.Model):
    __tablename__ = "ad_requests"
    id = db.Column(db.Integer(), primary_key=True)
    campaign_id = db.Column(db.Integer(), db.ForeignKey('campaign.id'))
    influencer_id = db.Column(db.Integer(), db.ForeignKey('influencers.id'))
    status = db.Column(db.String(24))
    messages = db.Column(db.String(540))
    requirements = db.Column(db.String(540))
    payment_amount = db.Column(db.Integer())
    campaign = db.relationship('Campaign', backref=db.backref('ad_requests', lazy=True))
    influencer = db.relationship('Influencers', backref=db.backref('ad_requests', lazy=True))

class CampaignReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencers.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Rating value (1 to 5)
    review_text = db.Column(db.Text, nullable=True)  # Optional review text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    influencer = db.relationship('Influencers', backref='campaign_reviews')
    campaign = db.relationship('Campaign', backref='reviews')


class InfluencerReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsors.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencers.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Rating value (1 to 5)
    review_text = db.Column(db.Text, nullable=True)  # Optional review text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sponsor = db.relationship('Sponsors', backref='influencer_reviews')
    influencer = db.relationship('Influencers', backref='reviews')
