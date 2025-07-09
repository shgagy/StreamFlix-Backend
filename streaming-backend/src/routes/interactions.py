from flask import Blueprint, jsonify, request
from src.models.user import db
from src.models.content import Content, Episode
from src.models.interactions import Rating, Comment, WatchHistory, Favorite, Notification
from src.routes.auth import token_required
from datetime import datetime

interactions_bp = Blueprint('interactions', __name__)

# Rating routes
@interactions_bp.route('/content/<int:content_id>/rating', methods=['POST'])
@token_required
def rate_content(current_user, content_id):
    try:
        content = Content.query.filter_by(id=content_id, is_active=True).first()
        if not content:
            return jsonify({'message': 'Content not found'}), 404
        
        data = request.get_json()
        if not data or 'score' not in data:
            return jsonify({'message': 'Rating score is required'}), 400
        
        score = data['score']
        if not isinstance(score, (int, float)) or score < 1 or score > 10:
            return jsonify({'message': 'Rating score must be between 1 and 10'}), 400
        
        # Check if user already rated this content
        existing_rating = Rating.query.filter_by(
            user_id=current_user.id,
            content_id=content_id
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.score = score
            existing_rating.updated_at = datetime.utcnow()
            message = 'Rating updated successfully'
        else:
            # Create new rating
            rating = Rating(
                user_id=current_user.id,
                content_id=content_id,
                score=score
            )
            db.session.add(rating)
            message = 'Rating added successfully'
        
        db.session.commit()
        
        # Recalculate content average rating
        content.calculate_average_rating()
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to rate content', 'error': str(e)}), 500

@interactions_bp.route('/content/<int:content_id>/rating', methods=['GET'])
@token_required
def get_user_rating(current_user, content_id):
    try:
        rating = Rating.query.filter_by(
            user_id=current_user.id,
            content_id=content_id
        ).first()
        
        if rating:
            return jsonify(rating.to_dict()), 200
        else:
            return jsonify({'message': 'No rating found'}), 404
            
    except Exception as e:
        return jsonify({'message': 'Failed to get rating', 'error': str(e)}), 500

@interactions_bp.route('/content/<int:content_id>/ratings', methods=['GET'])
def get_content_ratings(content_id):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        
        pagination = Rating.query.filter_by(content_id=content_id).order_by(
            Rating.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        ratings = pagination.items
        
        return jsonify({
            'ratings': [rating.to_dict() for rating in ratings],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get ratings', 'error': str(e)}), 500

# Comment routes
@interactions_bp.route('/content/<int:content_id>/comments', methods=['POST'])
@token_required
def add_comment(current_user, content_id):
    try:
        content = Content.query.filter_by(id=content_id, is_active=True).first()
        if not content:
            return jsonify({'message': 'Content not found'}), 404
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'message': 'Comment text is required'}), 400
        
        text = data['text'].strip()
        if len(text) < 1:
            return jsonify({'message': 'Comment cannot be empty'}), 400
        
        comment = Comment(
            user_id=current_user.id,
            content_id=content_id,
            text=text,
            parent_id=data.get('parent_id')
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Comment added successfully',
            'comment': comment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to add comment', 'error': str(e)}), 500

@interactions_bp.route('/content/<int:content_id>/comments', methods=['GET'])
def get_comments(content_id):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 50)
        
        # Get top-level comments (no parent)
        pagination = Comment.query.filter_by(
            content_id=content_id,
            parent_id=None,
            is_active=True
        ).order_by(Comment.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        comments = pagination.items
        
        return jsonify({
            'comments': [comment.to_dict(include_replies=True) for comment in comments],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get comments', 'error': str(e)}), 500

@interactions_bp.route('/comments/<int:comment_id>', methods=['PUT'])
@token_required
def update_comment(current_user, comment_id):
    try:
        comment = Comment.query.filter_by(id=comment_id, user_id=current_user.id).first()
        if not comment:
            return jsonify({'message': 'Comment not found or unauthorized'}), 404
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'message': 'Comment text is required'}), 400
        
        text = data['text'].strip()
        if len(text) < 1:
            return jsonify({'message': 'Comment cannot be empty'}), 400
        
        comment.text = text
        comment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Comment updated successfully',
            'comment': comment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update comment', 'error': str(e)}), 500

@interactions_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@token_required
def delete_comment(current_user, comment_id):
    try:
        comment = Comment.query.filter_by(id=comment_id, user_id=current_user.id).first()
        if not comment:
            return jsonify({'message': 'Comment not found or unauthorized'}), 404
        
        # Soft delete
        comment.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Comment deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete comment', 'error': str(e)}), 500

# Watch history routes
@interactions_bp.route('/watch-history', methods=['POST'])
@token_required
def update_watch_history(current_user):
    try:
        data = request.get_json()
        
        required_fields = ['content_id', 'watch_time', 'total_time']
        if not data or not all(k in data for k in required_fields):
            return jsonify({'message': 'content_id, watch_time, and total_time are required'}), 400
        
        content_id = data['content_id']
        episode_id = data.get('episode_id')
        watch_time = data['watch_time']
        total_time = data['total_time']
        
        # Validate content exists
        content = Content.query.filter_by(id=content_id, is_active=True).first()
        if not content:
            return jsonify({'message': 'Content not found'}), 404
        
        # Validate episode if provided
        if episode_id:
            episode = Episode.query.filter_by(id=episode_id, series_id=content_id, is_active=True).first()
            if not episode:
                return jsonify({'message': 'Episode not found'}), 404
        
        # Find existing watch history
        watch_history = WatchHistory.query.filter_by(
            user_id=current_user.id,
            content_id=content_id,
            episode_id=episode_id
        ).first()
        
        if watch_history:
            # Update existing record
            watch_history.watch_time = watch_time
            watch_history.total_time = total_time
            watch_history.completed = watch_time >= total_time * 0.9  # 90% completion
            watch_history.last_watched = datetime.utcnow()
        else:
            # Create new record
            watch_history = WatchHistory(
                user_id=current_user.id,
                content_id=content_id,
                episode_id=episode_id,
                watch_time=watch_time,
                total_time=total_time,
                completed=watch_time >= total_time * 0.9
            )
            db.session.add(watch_history)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Watch history updated successfully',
            'watch_history': watch_history.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update watch history', 'error': str(e)}), 500

@interactions_bp.route('/watch-history', methods=['GET'])
@token_required
def get_watch_history(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 50)
        
        pagination = WatchHistory.query.filter_by(user_id=current_user.id).order_by(
            WatchHistory.last_watched.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        history = pagination.items
        
        return jsonify({
            'watch_history': [item.to_dict() for item in history],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get watch history', 'error': str(e)}), 500

# Favorites routes
@interactions_bp.route('/favorites', methods=['POST'])
@token_required
def add_favorite(current_user):
    try:
        data = request.get_json()
        if not data or 'content_id' not in data:
            return jsonify({'message': 'content_id is required'}), 400
        
        content_id = data['content_id']
        
        # Validate content exists
        content = Content.query.filter_by(id=content_id, is_active=True).first()
        if not content:
            return jsonify({'message': 'Content not found'}), 404
        
        # Check if already in favorites
        existing_favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            content_id=content_id
        ).first()
        
        if existing_favorite:
            return jsonify({'message': 'Content already in favorites'}), 409
        
        favorite = Favorite(
            user_id=current_user.id,
            content_id=content_id
        )
        
        db.session.add(favorite)
        db.session.commit()
        
        return jsonify({
            'message': 'Added to favorites successfully',
            'favorite': favorite.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to add favorite', 'error': str(e)}), 500

@interactions_bp.route('/favorites', methods=['GET'])
@token_required
def get_favorites(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 50)
        
        pagination = Favorite.query.filter_by(user_id=current_user.id).order_by(
            Favorite.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        favorites = pagination.items
        
        return jsonify({
            'favorites': [item.to_dict() for item in favorites],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get favorites', 'error': str(e)}), 500

@interactions_bp.route('/favorites/<int:content_id>', methods=['DELETE'])
@token_required
def remove_favorite(current_user, content_id):
    try:
        favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            content_id=content_id
        ).first()
        
        if not favorite:
            return jsonify({'message': 'Favorite not found'}), 404
        
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({'message': 'Removed from favorites successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to remove favorite', 'error': str(e)}), 500

@interactions_bp.route('/favorites/<int:content_id>/check', methods=['GET'])
@token_required
def check_favorite(current_user, content_id):
    try:
        favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            content_id=content_id
        ).first()
        
        return jsonify({'is_favorite': favorite is not None}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to check favorite', 'error': str(e)}), 500

# Notifications routes
@interactions_bp.route('/notifications', methods=['GET'])
@token_required
def get_notifications(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 50)
        unread_only = request.args.get('unread_only', type=bool)
        
        query = Notification.query.filter_by(user_id=current_user.id)
        if unread_only:
            query = query.filter_by(is_read=False)
        
        pagination = query.order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        notifications = pagination.items
        
        return jsonify({
            'notifications': [notification.to_dict() for notification in notifications],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get notifications', 'error': str(e)}), 500

@interactions_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@token_required
def mark_notification_read(current_user, notification_id):
    try:
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user.id
        ).first()
        
        if not notification:
            return jsonify({'message': 'Notification not found'}), 404
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({'message': 'Notification marked as read'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to mark notification as read', 'error': str(e)}), 500

