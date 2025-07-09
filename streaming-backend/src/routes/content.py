from flask import Blueprint, jsonify, request
from src.models.user import db
from src.models.content import Content, Episode, Genre, content_genres
from src.models.interactions import Rating, Comment, WatchHistory, Favorite
from src.routes.auth import token_required, admin_required
from sqlalchemy import or_, and_, func
from datetime import datetime

content_bp = Blueprint('content', __name__)

@content_bp.route('/content', methods=['GET'])
def get_content():
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        content_type = request.args.get('type')  # 'movie' or 'series'
        genre_id = request.args.get('genre_id', type=int)
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'created_at')  # created_at, rating, view_count, title
        order = request.args.get('order', 'desc')  # asc or desc
        featured = request.args.get('featured', type=bool)
        
        # Build query
        query = Content.query.filter_by(is_active=True)
        
        if content_type:
            query = query.filter_by(content_type=content_type)
        
        if genre_id:
            query = query.filter(Content.genres.any(Genre.id == genre_id))
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(or_(
                Content.title.ilike(search_term),
                Content.description.ilike(search_term),
                Content.director.ilike(search_term),
                Content.cast.ilike(search_term)
            ))
        
        if featured is not None:
            query = query.filter_by(is_featured=featured)
        
        # Sorting
        if sort_by == 'rating':
            if order == 'desc':
                query = query.order_by(Content.rating.desc())
            else:
                query = query.order_by(Content.rating.asc())
        elif sort_by == 'view_count':
            if order == 'desc':
                query = query.order_by(Content.view_count.desc())
            else:
                query = query.order_by(Content.view_count.asc())
        elif sort_by == 'title':
            if order == 'desc':
                query = query.order_by(Content.title.desc())
            else:
                query = query.order_by(Content.title.asc())
        else:  # created_at
            if order == 'desc':
                query = query.order_by(Content.created_at.desc())
            else:
                query = query.order_by(Content.created_at.asc())
        
        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        content_list = pagination.items
        
        return jsonify({
            'content': [item.to_dict() for item in content_list],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch content', 'error': str(e)}), 500

@content_bp.route('/content/<int:content_id>', methods=['GET'])
def get_content_detail(content_id):
    try:
        content = Content.query.filter_by(id=content_id, is_active=True).first()
        if not content:
            return jsonify({'message': 'Content not found'}), 404
        
        # Increment view count
        content.view_count += 1
        db.session.commit()
        
        return jsonify(content.to_dict(include_episodes=True)), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch content', 'error': str(e)}), 500

@content_bp.route('/content', methods=['POST'])
@token_required
@admin_required
def create_content(current_user):
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'content_type']
        if not data or not all(k in data for k in required_fields):
            return jsonify({'message': 'Title and content_type are required'}), 400
        
        if data['content_type'] not in ['movie', 'series']:
            return jsonify({'message': 'content_type must be movie or series'}), 400
        
        # Create content
        content = Content(
            title=data['title'],
            description=data.get('description'),
            content_type=data['content_type'],
            cover_image=data.get('cover_image'),
            trailer_url=data.get('trailer_url'),
            release_year=data.get('release_year'),
            duration=data.get('duration'),
            imdb_rating=data.get('imdb_rating'),
            language=data.get('language'),
            country=data.get('country'),
            director=data.get('director'),
            cast=data.get('cast'),
            is_featured=data.get('is_featured', False),
            video_url=data.get('video_url')  # For movies
        )
        
        db.session.add(content)
        db.session.flush()  # Get the ID
        
        # Add genres
        if 'genre_ids' in data:
            genres = Genre.query.filter(Genre.id.in_(data['genre_ids'])).all()
            content.genres = genres
        
        db.session.commit()
        
        return jsonify({
            'message': 'Content created successfully',
            'content': content.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create content', 'error': str(e)}), 500

@content_bp.route('/content/<int:content_id>', methods=['PUT'])
@token_required
@admin_required
def update_content(current_user, content_id):
    try:
        content = Content.query.get_or_404(content_id)
        data = request.get_json()
        
        # Update fields
        updatable_fields = [
            'title', 'description', 'cover_image', 'trailer_url', 'release_year',
            'duration', 'imdb_rating', 'language', 'country', 'director', 'cast',
            'is_featured', 'is_active', 'video_url'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(content, field, data[field])
        
        # Update genres
        if 'genre_ids' in data:
            genres = Genre.query.filter(Genre.id.in_(data['genre_ids'])).all()
            content.genres = genres
        
        content.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Content updated successfully',
            'content': content.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update content', 'error': str(e)}), 500

@content_bp.route('/content/<int:content_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_content(current_user, content_id):
    try:
        content = Content.query.get_or_404(content_id)
        
        # Soft delete
        content.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Content deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete content', 'error': str(e)}), 500

# Episode routes
@content_bp.route('/content/<int:content_id>/episodes', methods=['GET'])
def get_episodes(content_id):
    try:
        content = Content.query.filter_by(id=content_id, content_type='series', is_active=True).first()
        if not content:
            return jsonify({'message': 'Series not found'}), 404
        
        season = request.args.get('season', type=int)
        
        query = Episode.query.filter_by(series_id=content_id, is_active=True)
        if season:
            query = query.filter_by(season_number=season)
        
        episodes = query.order_by(Episode.season_number, Episode.episode_number).all()
        
        return jsonify([episode.to_dict() for episode in episodes]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch episodes', 'error': str(e)}), 500

@content_bp.route('/content/<int:content_id>/episodes', methods=['POST'])
@token_required
@admin_required
def create_episode(current_user, content_id):
    try:
        content = Content.query.filter_by(id=content_id, content_type='series').first()
        if not content:
            return jsonify({'message': 'Series not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'episode_number', 'season_number']
        if not data or not all(k in data for k in required_fields):
            return jsonify({'message': 'Title, episode_number, and season_number are required'}), 400
        
        # Check for duplicate episode
        existing_episode = Episode.query.filter_by(
            series_id=content_id,
            season_number=data['season_number'],
            episode_number=data['episode_number']
        ).first()
        
        if existing_episode:
            return jsonify({'message': 'Episode already exists'}), 409
        
        episode = Episode(
            series_id=content_id,
            title=data['title'],
            description=data.get('description'),
            episode_number=data['episode_number'],
            season_number=data['season_number'],
            duration=data.get('duration'),
            video_url=data.get('video_url'),
            thumbnail=data.get('thumbnail'),
            air_date=datetime.strptime(data['air_date'], '%Y-%m-%d').date() if data.get('air_date') else None
        )
        
        db.session.add(episode)
        db.session.commit()
        
        return jsonify({
            'message': 'Episode created successfully',
            'episode': episode.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create episode', 'error': str(e)}), 500

# Genre routes
@content_bp.route('/genres', methods=['GET'])
def get_genres():
    try:
        genres = Genre.query.all()
        return jsonify([genre.to_dict() for genre in genres]), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch genres', 'error': str(e)}), 500

@content_bp.route('/genres', methods=['POST'])
@token_required
@admin_required
def create_genre(current_user):
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'message': 'Genre name is required'}), 400
        
        # Check if genre already exists
        existing_genre = Genre.query.filter_by(name=data['name']).first()
        if existing_genre:
            return jsonify({'message': 'Genre already exists'}), 409
        
        genre = Genre(
            name=data['name'],
            description=data.get('description')
        )
        
        db.session.add(genre)
        db.session.commit()
        
        return jsonify({
            'message': 'Genre created successfully',
            'genre': genre.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create genre', 'error': str(e)}), 500

# Search and recommendations
@content_bp.route('/search', methods=['GET'])
def search_content():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'message': 'Search query is required'}), 400
        
        search_term = f"%{query}%"
        content = Content.query.filter(
            and_(
                Content.is_active == True,
                or_(
                    Content.title.ilike(search_term),
                    Content.description.ilike(search_term),
                    Content.director.ilike(search_term),
                    Content.cast.ilike(search_term)
                )
            )
        ).order_by(Content.view_count.desc()).limit(20).all()
        
        return jsonify([item.to_dict() for item in content]), 200
        
    except Exception as e:
        return jsonify({'message': 'Search failed', 'error': str(e)}), 500

@content_bp.route('/recommendations', methods=['GET'])
@token_required
def get_recommendations(current_user):
    try:
        # Simple recommendation based on user's watch history and ratings
        # Get user's favorite genres from watch history
        user_genres = db.session.query(Genre.id).join(
            content_genres
        ).join(Content).join(WatchHistory).filter(
            WatchHistory.user_id == current_user.id
        ).distinct().all()
        
        genre_ids = [g[0] for g in user_genres]
        
        if genre_ids:
            # Recommend content from favorite genres
            recommendations = Content.query.filter(
                and_(
                    Content.is_active == True,
                    Content.genres.any(Genre.id.in_(genre_ids)),
                    ~Content.id.in_(
                        db.session.query(WatchHistory.content_id).filter_by(user_id=current_user.id)
                    )
                )
            ).order_by(Content.rating.desc(), Content.view_count.desc()).limit(10).all()
        else:
            # Fallback to popular content
            recommendations = Content.query.filter_by(is_active=True).order_by(
                Content.rating.desc(), Content.view_count.desc()
            ).limit(10).all()
        
        return jsonify([item.to_dict() for item in recommendations]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get recommendations', 'error': str(e)}), 500

