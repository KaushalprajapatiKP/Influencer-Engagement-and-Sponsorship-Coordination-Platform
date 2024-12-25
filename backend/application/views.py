from flask import Blueprint, request, jsonify
from flask_caching import Cache
from flask_security import login_user, current_user, auth_required, roles_required
from .models import db, User,  Sponsors, Influencers, Admin, Pending_Sponsors, Campaign, AdRequests, CampaignReview, InfluencerReview
from werkzeug.security import generate_password_hash, check_password_hash
from .sec import datastore
from datetime import datetime



api = Blueprint("api", __name__, url_prefix="/api")
cache = Cache()

@api.route('/login', methods=['POST'])
def login():
    '''This method is used for role based login'''
    front_end_data = request.get_json()
    email = front_end_data.get('email')
    password = front_end_data.get('password')
    role = front_end_data.get('role')

    # For sponsor role, check if user is already registered and password entered is correct
    if role == 'sponsor':
        sponsor = Sponsors.query.filter_by(email=email).first()
        if sponsor and check_password_hash(sponsor.password, password):
            login_user(sponsor.user)
            return jsonify({'user_id': sponsor.user.id, 'role': 'sponsor'}), 200

    # For influencer role, check if user is already registered and password entered is correct
    elif role == 'influencer':
        influencer = Influencers.query.filter_by(email=email).first()
        if influencer and check_password_hash(influencer.password, password):
            login_user(influencer.user)
            return jsonify({'user_id': influencer.user.id, 'role': 'influencer'}), 200

    # For admin role, check if user is already registered and password entered is correct
    elif role == 'admin':
        admin = Admin.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin.user)
            return jsonify({'user_id': admin.user.id, 'role': 'admin'}), 200

    return jsonify({"msg": "Invalid username, password, or role"}), 401

@api.route('/register-sponsor', methods=['POST'])
def register_sponsor():
    '''This method is used for registering a sponsor'''
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    company_name = data.get('companyName')
    industry_name = data.get('industryName')
    budget = data.get('budget')
    try:
        pending_sponsor = Pending_Sponsors(
            email=email,
            password=generate_password_hash(password),
            name=name,
            company_name=company_name,
            industry_name=industry_name,
            budget=budget,
        )
        db.session.add(pending_sponsor)
        db.session.commit()
        cache.clear()

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Registration failed", "error": str(e)}), 500
    return jsonify({"msg": "Sponsor registration request submitted successfully!"}), 201


@api.route('/register-influencer', methods=['POST'])
def register_influencer():
    '''This method is used for registering an influencer'''
    data = request.get_json()
    password = data.get('password')
    name = data.get('name')
    category = data.get('category')
    niche = data.get('niche')
    followers = data.get('followers') 
    email = data.get('email')

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already registered"}), 400

    hashed_password = generate_password_hash(password)
    user = datastore.create_user(name=name, email=email, password=hashed_password, active=True)
    role = datastore.find_or_create_role('influencer')
    datastore.add_role_to_user(user, role)

    influencer = Influencers(
        email=email,
        password=hashed_password,
        name=name,
        category=category,
        niche=niche,
        followers=followers, 
        user_id=user.id
    )
    
    db.session.add(influencer)
    try:
        db.session.commit()
        cache.clear()
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Registration failed", "error": str(e)}), 500

    return jsonify({"msg": "Influencer registered successfully"}), 201

@api.route('/pending-sponsors', methods=['GET'])
@cache.cached(90)
def get_pending_sponsors():
    ''' This method checks for if any sponsors are pending for approval of admin and returns list of all pending
    sponsors.'''
    pending_sponsors = Pending_Sponsors.query.all()
    result = [
        {
            "id": sponsor.id,
            "email": sponsor.email,
            "name": sponsor.name,
            "company_name": sponsor.company_name,
            "industry_name": sponsor.industry_name,
            "budget": sponsor.budget
        } for sponsor in pending_sponsors
    ]

    return jsonify(result), 200

@api.route('/approve-sponsor/<int:sponsor_id>', methods=['POST'])
# @roles_required("admin")
def approve_sponsor(sponsor_id):
    '''This method is used for approving a sponsor via admin dashboard'''
    pending_sponsor = Pending_Sponsors.query.get(sponsor_id)
    if not pending_sponsor:
        return jsonify({"msg": "Sponsor not found"}), 404
    
    try:
        user = datastore.create_user(
            name=pending_sponsor.name,
            email=pending_sponsor.email,
            password=pending_sponsor.password,
            active=True
        )
        role = datastore.find_or_create_role('sponsor')
        datastore.add_role_to_user(user, role)

        sponsor = Sponsors(
            email=pending_sponsor.email,
            password=pending_sponsor.password,
            name=pending_sponsor.name,
            company_name=pending_sponsor.company_name,
            industry_name=pending_sponsor.industry_name,
            budget=pending_sponsor.budget,
            user_id=user.id
        )
        db.session.add(sponsor)
        db.session.delete(pending_sponsor)
        db.session.commit()
        cache.clear()
        return jsonify({"msg": "Sponsor approved successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Failed to approve sponsor", "error": str(e)}), 500

@api.route('/reject-sponsor/<int:sponsor_id>', methods=['POST'])
# @roles_required("admin")
def reject_sponsor(sponsor_id):
    '''This method is used for rejecting a sponsor via admin dashboard'''
    pending_sponsor = Pending_Sponsors.query.get(sponsor_id)
    if not pending_sponsor:
        return jsonify({"msg": "Sponsor not found"}), 404
    try:
        db.session.delete(pending_sponsor)
        db.session.commit()
        cache.clear()
        return jsonify({"msg": "Sponsor rejected successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Failed to reject sponsor", "error": str(e)}), 500

@api.route('/sponsor/<int:id>', methods=['GET'])
@cache.cached(90)
def get_sponsor(id):
    '''This method returns the details of a sponsor via sponsor_id'''
    sponsor = Sponsors.query.filter_by(user_id=id).first_or_404()
    return jsonify({
        'id': sponsor.id,
        'name': sponsor.name,
        'email': sponsor.email,
        'companyName': sponsor.company_name,
        'industryName': sponsor.industry_name,
        'budget': sponsor.budget
    })

@api.route('/sponsor/<int:id>', methods=['PUT'])
# @roles_required("sponsor")
def update_sponsor(id):
    '''This method updates the details of a sponsor via sponsor_id'''
    data = request.get_json()
    sponsor = Sponsors.query.filter_by(user_id=id).first_or_404()
    sponsor.name = data.get('name', sponsor.name)
    sponsor.email = data.get('email', sponsor.email)
    sponsor.company_name = data.get('companyName', sponsor.company_name)
    sponsor.industry_name = data.get('industryName', sponsor.industry_name)
    sponsor.budget = data.get('budget', sponsor.budget)
    db.session.commit()
    cache.clear()
    return jsonify({'msg': 'Sponsor profile updated successfully'})


@api.route('/campaign', methods=['POST'])
# @roles_required("sponsor")
def create_campaign():
    '''This method creates a new campaign'''
    data = request.get_json()
    visibility = False
    if data.get('visibility') == 'public':
        visibility = True

    new_campaign = Campaign(
        name=data.get('name'),
        description=data.get('description'),
        budget=data.get('budget'),
        start_date= datetime.strptime(data.get('start_date'), '%Y-%m-%d').date(),
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date(),
        sponsor_id=data.get('sponsor_id'),
        visibility=visibility,
        goals = data.get('goals')
    )

    db.session.add(new_campaign)
    db.session.commit()
    cache.clear()
    return jsonify({"msg": "Campaign created successfully"}), 201

@api.route('/campaigns/<int:campaign_id>/flag', methods=['POST'])
# @roles_required('admin') 
def flag_campaign(campaign_id):
    '''This method flags a campaign as inappropriate via admin'''
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return jsonify({'msg': 'Campaign not found'}), 404
    campaign.flagged = True
    db.session.commit()
    cache.clear()
    return jsonify({'msg': 'Campaign flagged as inappropriate'}), 200

@api.route('/campaigns/<int:campaign_id>/unflag', methods=['POST'])
# @roles_required('admin') 
def unflag_campaign(campaign_id):
    '''This method unflags a campaign which is flagged as inappropriate via admin'''
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return jsonify({"error": "Campaign not found."}), 404
    campaign.flagged = False
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Campaign unflagged successfully."}), 200


@api.route('/campaigns/flagged_stats', methods=['GET'])
@cache.cached(90)
def get_flagged_campaigns_stats():
    '''This method returns the count of flagged and unflagged campaigns'''
    flagged_count = Campaign.query.filter_by(flagged=True).count()
    
    unflagged_count = Campaign.query.filter_by(flagged=False).count()
    return jsonify({
        'flagged': flagged_count,
        'unflagged': unflagged_count
    })

@api.route('/sponsor/<int:user_id>', methods=['GET'])
@cache.cached(90)
def get_sponsor_id(user_id):
    '''This method returns the sponsor_id associated with a user_id'''
    sponsor = db.session.query(Sponsors).filter_by(user_id=user_id).first()
    if sponsor:
        return jsonify({'sponsor_id': sponsor.id})
    else:
        return jsonify({'error': 'Sponsor not found'}), 404

@api.route('/campaigns_by_sponsor_id/<int:sponsor_id>', methods=['GET'])
@cache.cached(90)
def get_campaigns_by_sponsorId(sponsor_id):
    '''This method returns the campaigns associated with a sponsor_id'''
    sponsor = Sponsors.query.filter_by(user_id = sponsor_id).first()
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
    result = [
        {
            "id": campaign.id,
            "name": campaign.name,
            "description": campaign.description,
            "budget": campaign.budget,
            "start_date": campaign.start_date,
            "end_date": campaign.end_date,
            "visibility": campaign.visibility,
            "goals": campaign.goals,
            "flagged" : campaign.flagged
        } for campaign in campaigns
    ]
    return jsonify(result), 200

@api.route('/campaigns_by_campaign_id/<int:campaign_id>', methods=['GET'])
@api.route('/influencer/campaigns_by_campaign_id/<int:campaign_id>', methods=['GET'])
@cache.cached(90)
def get_campaigns_by_campaignsId(campaign_id):
    '''This method returns the details of a campaign via campaign_id'''
    campaign = Campaign.query.get(campaign_id)
    if campaign is None:
        return jsonify({'msg': 'Campaign not found'}), 404
    
    return jsonify({
        'id': campaign.id,
        'name': campaign.name,
        'description': campaign.description,
        'budget': campaign.budget,
        'start_date': campaign.start_date.strftime('%Y-%m-%d'),
        'end_date': campaign.end_date.strftime('%Y-%m-%d'),
        'visibility': campaign.visibility,
        'goals': campaign.goals,
        'flagged': campaign.flagged
    })

@api.route('/campaigns_by_campaign_id/<int:id>', methods=['PUT'])
# @roles_required('sponsor')  
def update_campaign(id):
    '''This method updates a campaign via campaign_id'''
    campaign = Campaign.query.get(id)
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404

    data = request.get_json()
    campaign.name = data.get('name')
    campaign.description = data.get('description')
    campaign.budget = data.get('budget')
    campaign.start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
    campaign.end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
    campaign.visibility = data.get('visibility')
    campaign.goals = data.get('goals')
    db.session.commit()
    cache.clear()
    return jsonify({'message': 'Campaign updated successfully'}), 200

@api.route('/campaigns_by_campaign_id/<int:id>', methods=['DELETE'])
# @roles_required('sponsor')  
def delete_campaign(id):
    '''This method deletes a campaign via campaign_id'''
    campaign = Campaign.query.get(id)
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404

    db.session.delete(campaign)
    db.session.commit()
    cache.clear()
    return jsonify({'message': 'Campaign deleted successfully'}), 200

@api.route('/ad-request', methods=['POST'])
def send_ad_request():
    '''This method sends an ad request to the influencer or sponsor'''
    data = request.get_json()
    influencer_id = data.get('influencer_id')
    campaign_id = data.get('campaign_id')
    status = data.get('status')
    messages = data.get('messages')
    requirements  = data.get('requirements', '')
    payment_amount = data.get('payment_amount', 0)

    ad_request = AdRequests(
        influencer_id=influencer_id,
        campaign_id=campaign_id,
        status=status,
        messages=messages,
        requirements=requirements,
        payment_amount=payment_amount,
    )
    db.session.add(ad_request)
    db.session.commit()
    cache.clear()
    return jsonify({"msg": "Ad request sent successfully"}), 201


@api.route('/ad-request/check', methods=['GET'])
def check_ad_request():
    '''This method checks if an ad request exists for a given campaign and influencer'''
    campaign_id = request.args.get('campaign_id')
    influencer_id = request.args.get('influencer_id')
    campaign_flagged = Campaign.query.filter_by(id=campaign_id).first()
    fg = campaign_flagged.flagged if campaign_flagged else False
    ad_request = AdRequests.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
    return jsonify({
        'exists': bool(ad_request),
        'flagged': fg
    })


@api.route('/ad-request/<int:ad_request_id>', methods=['GET'])
@cache.cached(90)
def get_ad_request(ad_request_id):
    '''This method returns the details of an ad request via ad_request_id'''
    ad_request = AdRequests.query.get_or_404(ad_request_id)
    campaign = Campaign.query.get_or_404(ad_request.campaign_id)
    sponsor = Sponsors.query.get_or_404(campaign.sponsor_id)
    ad_request_data = {
        'id': ad_request.id,
        'campaign_name': campaign.name,
        'sponsor_name' :sponsor.name,
        'influencer_id': ad_request.influencer_id,
        'sponsor_id': sponsor.id,
        'status': ad_request.status,
        'messages': ad_request.messages,
        'requirements': ad_request.requirements,
        'payment_amount': ad_request.payment_amount
    }
    return jsonify(ad_request_data), 200

@api.route('/ad-request/<int:ad_request_id>', methods=['PUT', 'POST'])
def accept_ad_request(ad_request_id):
    '''This method accepts an ad request via ad_request_id'''
    ad_request = AdRequests.query.get_or_404(ad_request_id)
    ad_request.status = 'accepted'
    campaign = Campaign.query.get_or_404(ad_request.campaign_id)
    campaign.budget_used = ad_request.payment_amount
    db.session.commit()
    cache.clear()
    return jsonify({"msg": "Ad request accepted successfully"}), 200


@api.route('/ad-request/<int:ad_request_id>', methods=['DELETE'])
def decline_ad_request(ad_request_id):
    '''This method declines an ad request via ad_request_id'''
    ad_request = AdRequests.query.get_or_404(ad_request_id)
    db.session.delete(ad_request)
    db.session.commit()
    cache.clear()
    return jsonify({"msg": "Ad request declined successfully"}), 200

@api.route('/ad-request/negotiate/<int:ad_request_id>', methods=['PUT'])
def negotiate_ad_request_inf(ad_request_id):
    '''This method negotiate an ad request via ad_request_id for influencer'''
    data = request.get_json()
    ad_request = AdRequests.query.get_or_404(ad_request_id)
    ad_request.payment_amount = data.get('payment_amount', ad_request.payment_amount)
    ad_request.status = 'Influencer-Negotiating'
    db.session.commit()
    cache.clear()
    return jsonify({"msg": "Ad request negotiation submitted successfully"}), 200

@api.route('/sponsor-negotiate/<int:ad_request_id>', methods=['PUT'])
def negotiate_ad_request_sp(ad_request_id):
    '''This method negotiate an ad request via ad_request_id for sponsor'''
    data = request.get_json()
    ad_request = AdRequests.query.get_or_404(ad_request_id)
    ad_request.payment_amount = data.get('payment_amount', ad_request.payment_amount)
    ad_request.status = 'Sponsor-Negotiating'
    db.session.commit()
    cache.clear()
    return jsonify({"msg": "Ad request negotiation submitted successfully"}), 200



@api.route('/influencers-list', methods=['GET'])
@cache.cached(90)
def get_influencers_list():
    '''This method returns a list of influencers'''
    influencers = Influencers.query.all()
    result = [
        {
            "id": influencer.id,
            "name": influencer.name,
            "email": influencer.email,
            "category": influencer.category,
            "niche": influencer.niche,
            "followers": influencer.followers,  
        } for influencer in influencers
    ]
    return jsonify(result), 200


@api.route('/influencers/<int:influencer_id>', methods=['GET'])
@cache.cached(90)
def get_influencer(influencer_id):
    '''This method returns the details of an influencer via influencer_id'''
    influencer = Influencers.query.filter_by(user_id=influencer_id).first_or_404()
    result ={
            "id": influencer.id,
            "name": influencer.name,
            "email": influencer.email,
            "category": influencer.category,
            "niche": influencer.niche,
            "followers": influencer.followers, 
            "user_id" : influencer.user_id
        }
    return jsonify(result)


@api.route('/influencers_sp/<int:influencer_id>', methods=['GET'])
@cache.cached(90)
def get_influencer_by_user_id(influencer_id):
    '''This method returns the details of an influencer via influencer_id'''
    influencer = Influencers.query.get_or_404(influencer_id)
    result ={
            "id": influencer.id,
            "name": influencer.name,
            "email": influencer.email,
            "category": influencer.category,
            "niche": influencer.niche,
            "followers": influencer.followers, 
            "user_id" : influencer.user_id
        }
    return jsonify(result)

@api.route('/influencers/<int:influencer_id>', methods=['PUT'])
# @roles_required('influencer')
def update_influencer_profile(influencer_id):
    '''This method updates the details of an influencer via influencer_id'''
    data = request.get_json()
    influencer = Influencers.query.filter_by(user_id=influencer_id).first_or_404()
    influencer.name = data.get('name', influencer.name)
    influencer.email = data.get('email', influencer.email)
    influencer.category = data.get('category', influencer.category)
    influencer.niche = data.get('niche', influencer.niche)
    influencer.followers = data.get('followers', influencer.followers)
    db.session.commit()
    cache.clear()
    return jsonify({'msg': 'Influencer profile updated successfully'}), 200
    
@api.route('/public-campaigns', methods=['GET'])
@cache.cached(90)
def get_public_campaigns():
    '''This method returns a list of public campaigns for influencer'''
    public_campaigns = db.session.query(Campaign, Sponsors.name.label('sponsor_name')).join(Sponsors).filter(Campaign.visibility == True).all()
    sponsor_id = []
    response = []
    for campaign, sponsor_name in public_campaigns:
        sponsor_id.append(campaign.sponsor_id)
        campaign_dict = {
            'id': campaign.id,
            'name': campaign.name,
            'description': campaign.description,
            'start_date': campaign.start_date.strftime('%Y-%m-%d'),
            'end_date': campaign.end_date.strftime('%Y-%m-%d'),
            'budget': campaign.budget,
            'goals': campaign.goals,
            'sponsor_name': sponsor_name,
            'flagged': campaign.flagged
        }
        response.append(campaign_dict)
    return jsonify(response)

@api.route('/influencer-ads', methods=['GET'])
@cache.cached(90)
def get_influencer_ads():
    '''This method returns a list of ads for an influencer'''
    user_id = request.args.get('influencer_id')
    try:
        influencer = db.session.query(Influencers).filter_by(user_id=user_id).first()
        influencer_id = influencer.id
        ad_requests = db.session.query(
            AdRequests,
            Campaign.name.label('campaign_name'),
            Sponsors.name.label('sponsor_name')
        ).join(Campaign, AdRequests.campaign_id == Campaign.id) \
         .join(Sponsors, Campaign.sponsor_id == Sponsors.id) \
         .filter(AdRequests.influencer_id == influencer_id) \
         .all()

        response = []
        for ad_request, campaign_title, sponsor_name in ad_requests:
            ad_request_dict = {
                'id': ad_request.id,
                'campaign_id': ad_request.campaign_id,
                'influencer_id': ad_request.influencer_id,
                'status': ad_request.status,
                'messages': ad_request.messages,
                'requirements': ad_request.requirements,
                'payment_amount': ad_request.payment_amount,
                'campaign_title': campaign_title,
                'sponsor_name': sponsor_name
            }
            response.append(ad_request_dict)
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': 'An internal error occurred'}), 500
    

@api.route('/sponsor-ads', methods=['GET'])
@cache.cached(90)
def get_sponsor_ads():
    '''This method returns a list of ads for a sponsor'''
    user_id = request.args.get('sponsor_id')
    try:
        sponsor = db.session.query(Sponsors).filter_by(user_id=user_id).first()
        sponsor_id = sponsor.id
        ad_requests = db.session.query(
        AdRequests,
        Campaign.name.label('campaign_name'),
        Sponsors.name.label('sponsor_name')
                ).join(Campaign, AdRequests.campaign_id == Campaign.id) \
                .join(Sponsors, Campaign.sponsor_id == Sponsors.id) \
                .filter(Sponsors.id == sponsor_id) \
                .all()

        response = []
        for ad_request, campaign_title, influencer_name in ad_requests:
            ad_request_dict = {
                'id': ad_request.id,
                'campaign_id': ad_request.campaign_id,
                'influencer_id': ad_request.influencer_id,
                'status': ad_request.status,
                'messages': ad_request.messages,
                'requirements': ad_request.requirements,
                'payment_amount': ad_request.payment_amount,
                'campaign_title': campaign_title,
                'influencer_name': influencer_name
            }
            response.append(ad_request_dict)
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': 'An internal error occurred'}), 500

@api.route('/search/campaigns', methods=['GET'])
def search_campaigns():
    '''This method returns a search-result list of campaigns for a sponsor'''
    query = request.args.get('query', '')
    user_id = request.args.get('sponsor_id')
    sponsor_id = (Sponsors.query.filter_by(user_id=user_id).first()).id
    if query:
        campaigns = Campaign.query.filter(
            Campaign.sponsor_id == sponsor_id,
            Campaign.name.ilike(f"%{query}%")
        ).all()
    else:
        campaigns = Campaign.query.filter(Campaign.sponsor_id == sponsor_id).all()

    response = []
    for campaign in campaigns:
        sponsor = Sponsors.query.get(campaign.sponsor_id)
        response.append({
            'id': campaign.id,
            'name': campaign.name,
            'description': campaign.description,
            'start_date': campaign.start_date.strftime('%Y-%m-%d') if campaign.start_date else None,
            'end_date': campaign.end_date.strftime('%Y-%m-%d') if campaign.end_date else None,
            'is_public': campaign.visibility,
            'budget': campaign.budget,
            'goals': campaign.goals,
            'sponsor_name': sponsor.name if sponsor else None,
            'flagged': campaign.flagged
        })

    return jsonify(response)

@api.route('/search/influencers', methods=['GET'])
def search_influencers():
    '''This method returns a search-result list of influencers for a sponsor and admin'''
    query = request.args.get('query', '')

    if query:
        influencers = Influencers.query.filter(
            Influencers.name.ilike(f"%{query}%"))
    else:
        influencers = Influencers.query.all()

    response = []
    for influencer in influencers:
        response.append({
            'id': influencer.id,
            'name': influencer.name,
            'email': influencer.email,
            'category': influencer.category,
            'niche': influencer.niche,
            'followers': influencer.followers, 
        })

    return jsonify(response)

@api.route('/search/public-campaigns', methods=['GET'])
def search_public_campaigns():
    '''This method returns a search-result list of public campaigns for influencer'''
    query = request.args.get('query')
    
    if query:
        campaigns = Campaign.query.filter(Campaign.visibility == True, Campaign.name.ilike(f'%{query}%')).all()
    else:
        campaigns = Campaign.query.filter(Campaign.visibility == True).all()
    
    result = []
    for campaign in campaigns:
        sponsor = Sponsors.query.get(campaign.sponsor_id)
        campaign_dict = {
            'id': campaign.id,
            'name': campaign.name,
            'description': campaign.description,
            'start_date': campaign.start_date.strftime('%Y-%m-%d') if campaign.start_date else None,
            'end_date': campaign.end_date.strftime('%Y-%m-%d') if campaign.end_date else None,
            'is_public': campaign.visibility,
            'budget': campaign.budget,
            'goals': campaign.goals,
            'sponsor_name': sponsor.name if sponsor else None,
            'flagged': campaign.flagged,
        }
        result.append(campaign_dict)

    return jsonify(result)
@api.route('/admin/search', methods=['GET'])
def admin_search():
    '''This method returns a search-result list of campaigns, influencers, and sponsors for admin'''
    search_type = request.args.get('type')
    query = request.args.get('query', '').strip()
    results = []
    if search_type == 'campaigns':
        if query:
            campaigns = Campaign.query.filter(Campaign.name.ilike(f'%{query}%')).all()
        else:
            campaigns = Campaign.query.all()
        
        result = []
        for campaign in campaigns:
            sponsor = Sponsors.query.get(campaign.sponsor_id)
            campaign_dict = {
                'id': campaign.id,
                'name': campaign.name,
                'description': campaign.description,
                'start_date': campaign.start_date.strftime('%Y-%m-%d') if campaign.start_date else None,
                'end_date': campaign.end_date.strftime('%Y-%m-%d') if campaign.end_date else None,
                'is_public': campaign.visibility,
                'budget': campaign.budget,
                'goals': campaign.goals,
                'sponsor_name': sponsor.name if sponsor else None,
                'flagged': campaign.flagged,
            }
            result.append(campaign_dict)
        results = result

    elif search_type == 'influencers':
        if query:
            influencers = Influencers.query.filter(Influencers.name.ilike(f'%{query}%')).all()
        else:
            influencers = Influencers.query.all()
        
        results = [{
            'id': influencer.id,
            'name': influencer.name,
            'email': influencer.email,
            'category': influencer.category,
            'niche': influencer.niche,
            'followers': influencer.followers, 
        } for influencer in influencers]

    elif search_type == 'sponsors':
        if query:
            sponsors = Sponsors.query.filter(Sponsors.name.ilike(f'%{query}%')).all()
        else:
            sponsors = Sponsors.query.all()
        
        results = [{
            'id': sponsor.id,
            'name': sponsor.name,
            'email': sponsor.email,
            'company_name': sponsor.company_name,
            'industry_name': sponsor.industry_name,
            'budget': sponsor.budget,
        } for sponsor in sponsors]

    return jsonify(results)


@api.route('/admin/influencers', methods=['GET'])
@cache.cached(90)
def get_influencers():
    '''This method gets list of all the influencers for the admin'''
    influencers = Influencers.query.all()
    results = [{
        'id': influencer.id,
        'name': influencer.name,
        'email': influencer.email,
        'category': influencer.category,
        'niche': influencer.niche,
        'followers': influencer.followers,
    } for influencer in influencers]
    return jsonify(results)

@api.route('/admin/sponsors', methods=['GET'])
@cache.cached(90)
def get_sponsors():
    '''This method gets list of all the sponsors for the admin'''
    sponsors = Sponsors.query.all()
    pending_sponsors = Pending_Sponsors.query.all()
    sponsor_results = [{
        'id': sponsor.id,
        'name': sponsor.name,
        'email': sponsor.email,
        'status': 'registered',
        'company_name': sponsor.company_name,
        'industry_name': sponsor.industry_name,
        'budget': sponsor.budget,
    } for sponsor in sponsors]
    
    pending_sponsor_results = [{
        'id': sponsor.id,
        'name': sponsor.name,
        'email': sponsor.email,
        'status': 'pending',
        'company_name': sponsor.company_name,
        'industry_name': sponsor.industry_name,
        'budget': sponsor.budget,
    } for sponsor in pending_sponsors]

    results = {
        'registered': sponsor_results,
        'pending': pending_sponsor_results
    }
    return jsonify(results)



@api.route('/admin/campaigns', methods=['GET'])
@cache.cached(90)
def get_campaigns():
    '''This method gets list of all the campaigns for the admin'''
    campaigns = Campaign.query.all()
    results = []
    for campaign in campaigns:
        sponsor = Sponsors.query.get(campaign.sponsor_id)
        campaign_dict = {
            'id': campaign.id,
            'name': campaign.name,
            'description': campaign.description,
            'start_date': campaign.start_date.strftime('%Y-%m-%d') if campaign.start_date else None,
            'end_date': campaign.end_date.strftime('%Y-%m-%d') if campaign.end_date else None,
            'is_public': campaign.visibility,
            'budget': campaign.budget,
            'goals': campaign.goals,
            'sponsor_name': sponsor.name if sponsor else None,
            'flagged' : campaign.flagged 
        }
        results.append(campaign_dict)
    return jsonify(results)


@api.route('/admin/follower-segments', methods=['GET'])
@cache.cached(90)
def get_follower_segments():
    '''This method is used for counting the number of influencers for follower segments and used in admin-stats'''
    follower_counts = {
        'Nano': Influencers.query.filter_by(followers='nano').count(),
        'Micro': Influencers.query.filter_by(followers='micro').count(),
        'Macro': Influencers.query.filter_by(followers='macro').count(),
        'Mega': Influencers.query.filter_by(followers='mega').count()
    }
    return jsonify(follower_counts)


@api.route('/sponsor/campaigns', methods=['GET'])
@cache.cached(90)
def get_sponsor_campaigns():
    '''This method retrives list of campaigns for the perticular sponsor'''
    campaigns = Campaign.query.all()
    campaign_list = [{
        'id': campaign.id,
        'name': campaign.name,
        'description': campaign.description,
        'start_date': campaign.start_date.strftime('%Y-%m-%d') if campaign.start_date else None,
        'end_date': campaign.end_date.strftime('%Y-%m-%d') if campaign.end_date else None,
        'budget': campaign.budget,
        'goals': campaign.goals,
        'is_public': campaign.visibility,
        'flagged' : campaign.flagged,
    } for campaign in campaigns]
    return jsonify(campaign_list)

@api.route('/sponsor/follower-segments', methods=['GET'])
@cache.cached(90)
def get_sponsor_follower_segments():
    '''This method is used for counting the number of influencers for follower segments and used in sponsor-stats'''
    follower_data = {
        'Nano': Influencers.query.filter_by(followers='nano').count(),
        'Micro': Influencers.query.filter_by(followers='micro').count(),
        'Macro': Influencers.query.filter_by(followers='macro').count(),
        'Mega': Influencers.query.filter_by(followers='mega').count(),
    }
    return jsonify(follower_data)

@api.route('/sponsor/niche-segments', methods=['GET'])
@cache.cached(90)
def get_sponsor_niche_segments():
    '''This method is used for finding niche counts of influencers for sponsor-stats'''
    niches = ['fashion', 'tech', 'fitness', 'travel', 'beauty', 'food', 'lifestyle', 'tech', 'gaming', 'parenting', 'finance']  
    niche_data = {niche: Influencers.query.filter_by(niche=niche).count() for niche in niches}
    return jsonify(niche_data)

@api.route('/sponsor/category-segments', methods=['GET'])
@cache.cached(90)
def get_sponsor_category_segments():
    '''This method is used for finding category counts of influencers for sponsor-stats'''
    categories = ['Beauty', 'Gaming', 'Food', 'Lifestyle'] 
    category_data = {category: Influencers.query.filter_by(category=category).count() for category in categories}
    return jsonify(category_data)

@api.route('/sponsor/requests-stats', methods=['GET'])
@cache.cached(90)
def get_requests_stats():
    '''This method is used for finding request stats for sponsor-stats'''
    accepted_requests = AdRequests.query.filter_by(status='accepted' ).count()
    pending_requests = AdRequests.query.filter(AdRequests.status != 'accepted' ).count()
    request_stats = {
        'accepted': accepted_requests,
        'pending': pending_requests,
    }
    return jsonify(request_stats)


@api.route('/campaigns/<int:campaign_id>/review-influencer', methods=['POST'])
def submit_campaign_review(campaign_id):
    '''This method is used for submitting review for a campaign'''
    influencer_id = request.json.get('influencer_id')
    rating = int(request.json.get('rating'))
    review_text = request.json.get('review_text', '')
    if not (1 <= rating <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    existing_review = CampaignReview.query.filter_by(influencer_id=influencer_id, campaign_id=campaign_id).first()

    if existing_review:
        existing_review.rating = rating
        existing_review.review_text = review_text
        db.session.commit()
        return jsonify({'message': 'Review updated successfully'}), 200
    else:
        new_review = CampaignReview(influencer_id=influencer_id, campaign_id=campaign_id, rating=rating, review_text=review_text)
        db.session.add(new_review)
        db.session.commit()
        cache.clear()
        return jsonify({'message': 'Review submitted successfully'}), 201
    


@api.route('/influencer-review/<int:influencer_id>', methods=['POST'])
def review_influencer(influencer_id):
    '''This method is used for submitting review for an influencer'''
    sponsor_id = request.json.get('sponsor_id')
    rating = int(request.json.get('rating'))
    review_text = request.json.get('review_text')
    if not (1 <= rating <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    existing_review = InfluencerReview.query.filter_by(sponsor_id=sponsor_id, influencer_id=influencer_id).first()

    if existing_review:
        existing_review.rating = rating
        existing_review.review_text = review_text
        db.session.commit()
        return jsonify({'message': 'Review updated successfully'}), 200
    else:
        new_review = InfluencerReview(sponsor_id=sponsor_id, influencer_id=influencer_id, rating=rating, review_text=review_text)
        db.session.add(new_review)
        db.session.commit()
        cache.clear()
        return jsonify({'message': 'Review submitted successfully'}), 201
