import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import OneHotEncoder
from nltk.stem import WordNetLemmatizer
import numpy as np
from .models import *
from django.core.cache import cache

#Load User, user preferences and opportunities from database.
def load_data(user):
    user_id = user.id
    user = User.objects.get(id=user_id)
    preferences = VolunteerPreferences.objects.filter(user_id=user_id).select_related('user').first()
    opportunities = VolunteerOpportunity.objects.only("id", "title", "description", "skills_required", "location", "commitment_level", "remote").all()
    return user, preferences, list(opportunities)

# Preprocesses data for matching users with volunteer opportunities.
def preprocess_data(user, preferences, opportunities):
    lemmatizer = WordNetLemmatizer()
    user_skills = {user.id: [lemmatizer.lemmatize(skill) for skill in preferences.skills] if preferences else []}
    user_location = {user.id: getattr(user, 'location', None)}
    opportunity_skills = {
        opp.id: [lemmatizer.lemmatize(skill) for skill in opp.skills_required] for opp in opportunities
    }
    opportunity_locations = {opp.id: opp.location for opp in opportunities}
    user_interests = {user.id: preferences.interests if preferences else []}
    return user_skills, user_location, opportunity_skills, opportunity_locations, user_interests


# Builds a user-opportunity interaction matrix, where rows represent users and columns represent opportunities. 
def build_interaction_matrix():
    # Fetch all users and opportunities
    users = User.objects.values_list('id', flat=True)
    opportunities = VolunteerOpportunity.objects.values_list('id', flat=True)

    # Fetch applications data
    applications = VolunteerApplications.objects.all()
    data = pd.DataFrame(list(applications.values('user_id', 'opportunity_id')))

    if data.empty or 'user' not in data.columns or 'opportunity_id' not in data.columns:
        return pd.DataFrame(index=users, columns=opportunities).fillna(0)

    # Build the interaction matrix
    interaction_matrix = data.pivot_table(index='user_id', columns='opportunity_id', aggfunc='size', fill_value=0)

    # Add missing users with default values
    for user_id in users:
        if user_id not in interaction_matrix.index:
            interaction_matrix.loc[user_id] = 0

    # Add missing opportunities with default values
    for opp_id in opportunities:
        if opp_id not in interaction_matrix.columns:
            interaction_matrix[opp_id] = 0

    # Ensure consistent sorting
    interaction_matrix = interaction_matrix.sort_index(axis=0).sort_index(axis=1)
    return interaction_matrix


#   Computes similarity scores between a user and available opportunities
def compute_similarity(users_skills, users_location, opportunities_skills, opportunities_location, users, user_interests):
    vectorizer = cache.get('tfidf_vectorizer')
    if vectorizer is None:
        vectorizer = TfidfVectorizer(stop_words='english')
        cache.set('tfidf_vectorizer', vectorizer, timeout=3600)

    # Precompute opportunity skills matrix
    opportunity_skills_text = [" ".join(skills) for skills in opportunities_skills.values()]
    if not any(opportunity_skills_text):
        return np.zeros(len(opportunities_skills))
    opportunity_skills_matrix = cache.get('opportunity_skills_matrix')
    if opportunity_skills_matrix is None:
        opportunity_skills_matrix = vectorizer.fit_transform(opportunity_skills_text)
        cache.set('opportunity_skills_matrix', opportunity_skills_matrix, timeout=3600)
    else:
        vectorizer.fit(opportunity_skills_text)
    
    user_skills_text = " ".join(users_skills[users.id])
    if not any(user_skills_text):
        return np.zeros(len(users_skills))
    user_skills_matrix = vectorizer.transform([user_skills_text])
    skills_similarity = cosine_similarity(user_skills_matrix, opportunity_skills_matrix)
    
    # Add user interests to similarity score
    user_interests_text = " ".join(user_interests[users.id])
    if not any(user_interests_text):
        return np.zeros(len(user_interests))
    if user_interests_text:
        user_interests_matrix = vectorizer.transform([user_interests_text])
        interest_similarity = cosine_similarity(user_interests_matrix, opportunity_skills_matrix)
    else:
        interest_similarity = np.zeros_like(skills_similarity)
    
    # Combine scores with weights
    location_similarity = np.array([
        1 if users_location[users.id] == opportunities_location[opp_id] else 0 for opp_id in opportunities_location
    ])
    combined_similarity = (
        0.5 * skills_similarity + 
        0.3 * location_similarity + 
        0.2 * interest_similarity
    )      
    return combined_similarity.flatten()


# Recommends the top opportunities for a user based on similarity scores.
def recommend_opportunities(similarity_scores, opportunities, threshold=0.004):

    if similarity_scores is None:
        return []  

    # Convert to NumPy array while handling None values
    similarity_scores = np.array([score if score is not None else -1 for score in similarity_scores])

    # Get indices where similarity score is above the threshold
    valid_indices = np.where(similarity_scores >= threshold)[0]

    # Sort valid indices by similarity score in descending order
    sorted_indices = valid_indices[np.argsort(similarity_scores[valid_indices])[::-1]]

    recommendations = []
    for idx in sorted_indices:
        opportunity = opportunities[int(idx)]
        recommendations.append({
            'title': opportunity.title,
            'description': opportunity.description,
            'skills_required': ", ".join(opportunity.skills_required),
            'location': opportunity.location,
            'commitment_level': opportunity.commitment_level,
            'remote': opportunity.remote,
            'id': opportunity.id 
        })

    return recommendations          


# Recommends opportunities for a user based on interaction data.
def recommend_collaborative(user_id, interaction_matrix, opportunities, top_n=3):
    # Ensure the user exists in the interaction matrix
    if user_id not in interaction_matrix.index:
        raise ValueError(f"user_id {user_id} not found in interaction matrix")
    
    if interaction_matrix.shape[0] == 0 or interaction_matrix.shape[1] == 0:
        return []  # No recommendations if there's no data
    
    # Recompute user similarity matrix if the matrix size has changed
    expected_size = interaction_matrix.shape[0]
    user_similarity = cache.get('user_similarity')
    if user_similarity is None or user_similarity.shape[0] != expected_size:
        user_similarity = cosine_similarity(interaction_matrix)
        cache.set('user_similarity', user_similarity, timeout=86400)
    
    # Get user index and compute scores
    user_index = interaction_matrix.index.get_loc(user_id)
    similar_users = user_similarity[user_index]
    scores = np.dot(similar_users, interaction_matrix.values)
    
    # Ensure top_n does not exceed available opportunities
    top_n = min(top_n, len(scores))
    
    # Get top N recommendations
    recommended_indices = np.argsort(scores)[-top_n:][::-1]
    recommended_opportunity_ids = interaction_matrix.columns[recommended_indices]
    
    # Build recommendations
    opportunity_lookup = {opp.id: opp for opp in opportunities}
    collaborative_recommendations = [
        {
            'title': opportunity_lookup[opp_id].title,
            'description': opportunity_lookup[opp_id].description,
            'skills_required': ", ".join(opportunity_lookup[opp_id].skills_required),
            'location': opportunity_lookup[opp_id].location,
            'commitment_level': opportunity_lookup[opp_id].commitment_level,
            'remote': opportunity_lookup[opp_id].remote,
            'id': opportunity_lookup[opp_id].id
        }
        for opp_id in recommended_opportunity_ids if opp_id in opportunity_lookup
    ]
    return collaborative_recommendations

