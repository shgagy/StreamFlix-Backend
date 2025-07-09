from flask import Blueprint, jsonify, request
from src.models.user import User, db
from src.models.content import Content, Episode, Genre
from src.models.interactions import Rating, Comment, WatchHistory, Favorite, Notification
from src.routes.auth import token_required, admin_required
from sqlalchemy import func, desc
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

# Dashboard statistics
@admin_bp.route('/dashboard/stats', methods=['GET'])
@token_required
@admin_required
def get_dashboard_stats(current_user):
    try:
        # Basic counts
        total_users = User.query.count()
        total_content = Content.query.filter_by(is_active=True).count()
        total_movies = Content.query.filter_by(content_type='movie', is_active=True).count()
        total_series = Content.query.filter_by(content_type='series', is_active=True).count()
        total_episodes = Episode.query.filter_by(is_active=True).count()
        
        # Active users (logged in within last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = User.query.filter(User.last_login >= thirty_days_ago).count()
        
        # Content views
        total_views = db.session.query(func.sum(Content.view_count)).scalar() or 0
        
        # Recent registrations (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        new_users = User.query.filter(User.created_at >= seven_days_ago).count()
        
        # Top content by views
        top_content = Content.query.filter_by(is_active=True).order_by(
            desc(Content.view_count)
        ).limit(5).all()
        
        # Recent comments
        recent_comments = Comment.query.filter_by(is_active=True).order_by(
            desc(Comment.created_at)
        ).limit(5).all()
        
        return jsonify({
            'stats': {
                'total_users': total_users,
                'active_users': active_users,
                'new_users_week': new_users,
                'total_content': total_content,
                'total_movies': total_movies,
                'total_series': total_series,
                'total_episodes': total_episodes,
                'total_views': total_views
            },
            'top_content': [content.to_dict() for content in top_content],
            'recent_comments': [comment.to_dict() for comment in recent_comments]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get dashboard stats', 'error': str(e)}), 500

# User management
@admin_bp.route('/users', methods=['GET'])
@token_required
@admin_required
def get_all_users(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search')
        status = request.args.get('status')  # 'active', 'inactive'
        
        query = User.query
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (User.username.ilike(search_term)) | 
                (User.email.ilike(search_term))
            )
        
        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)
        
        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users = pagination.items
        
        return jsonify({
            'users': [user.to_dict() for user in users],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get users', 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
@admin_required
def get_user_detail(current_user, user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        # Get user statistics
        watch_count = WatchHistory.query.filter_by(user_id=user_id).count()
        favorite_count = Favorite.query.filter_by(user_id=user_id).count()
        rating_count = Rating.query.filter_by(user_id=user_id).count()
        comment_count = Comment.query.filter_by(user_id=user_id, is_active=True).count()
        
        user_data = user.to_dict()
        user_data['statistics'] = {
            'watch_count': watch_count,
            'favorite_count': favorite_count,
            'rating_count': rating_count,
            'comment_count': comment_count
        }
        
        return jsonify(user_data), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get user details', 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@token_required
@admin_required
def toggle_user_status(current_user, user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent admin from deactivating themselves
        if user.id == current_user.id:
            return jsonify({'message': 'Cannot deactivate your own account'}), 400
        
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        return jsonify({
            'message': f'User {status} successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to toggle user status', 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/make-admin', methods=['POST'])
@token_required
@admin_required
def make_user_admin(current_user, user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        user.is_admin = True
        db.session.commit()
        
        return jsonify({
            'message': 'User promoted to admin successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to make user admin', 'error': str(e)}), 500

# Content management
@admin_bp.route('/content/all', methods=['GET'])
@token_required
@admin_required
def get_all_content(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        content_type = request.args.get('type')
        status = request.args.get('status')  # 'active', 'inactive'
        search = request.args.get('search')
        
        query = Content.query
        
        if content_type:
            query = query.filter_by(content_type=content_type)
        
        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(Content.title.ilike(search_term))
        
        pagination = query.order_by(Content.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        content_list = pagination.items
        
        return jsonify({
            'content': [item.to_dict() for item in content_list],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get content', 'error': str(e)}), 500

@admin_bp.route('/content/<int:content_id>/toggle-status', methods=['POST'])
@token_required
@admin_required
def toggle_content_status(current_user, content_id):
    try:
        content = Content.query.get_or_404(content_id)
        
        content.is_active = not content.is_active
        content.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = 'activated' if content.is_active else 'deactivated'
        return jsonify({
            'message': f'Content {status} successfully',
            'content': content.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to toggle content status', 'error': str(e)}), 500

@admin_bp.route('/content/<int:content_id>/toggle-featured', methods=['POST'])
@token_required
@admin_required
def toggle_content_featured(current_user, content_id):
    try:
        content = Content.query.get_or_404(content_id)
        
        content.is_featured = not content.is_featured
        content.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = 'featured' if content.is_featured else 'unfeatured'
        return jsonify({
            'message': f'Content {status} successfully',
            'content': content.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to toggle content featured status', 'error': str(e)}), 500

# Comment moderation
@admin_bp.route('/comments', methods=['GET'])
@token_required
@admin_required
def get_all_comments(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')  # 'active', 'inactive'
        
        query = Comment.query
        
        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)
        
        pagination = query.order_by(Comment.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        comments = pagination.items
        
        return jsonify({
            'comments': [comment.to_dict() for comment in comments],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get comments', 'error': str(e)}), 500

@admin_bp.route('/comments/<int:comment_id>/toggle-status', methods=['POST'])
@token_required
@admin_required
def toggle_comment_status(current_user, comment_id):
    try:
        comment = Comment.query.get_or_404(comment_id)
        
        comment.is_active = not comment.is_active
        comment.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = 'activated' if comment.is_active else 'deactivated'
        return jsonify({
            'message': f'Comment {status} successfully',
            'comment': comment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to toggle comment status', 'error': str(e)}), 500

# Analytics
@admin_bp.route('/analytics/content-views', methods=['GET'])
@token_required
@admin_required
def get_content_analytics(current_user):
    try:
        days = request.args.get('days', 30, type=int)
        
        # Top content by views
        top_content = Content.query.filter_by(is_active=True).order_by(
            desc(Content.view_count)
        ).limit(10).all()
        
        # Content by type
        content_by_type = db.session.query(
            Content.content_type,
            func.count(Content.id).label('count')
        ).filter_by(is_active=True).group_by(Content.content_type).all()
        
        # Content by genre
        content_by_genre = db.session.query(
            Genre.name,
            func.count(Content.id).label('count')
        ).join(Content.genres).filter(Content.is_active == True).group_by(Genre.name).all()
        
        return jsonify({
            'top_content': [
                {
                    'title': content.title,
                    'view_count': content.view_count,
                    'content_type': content.content_type
                } for content in top_content
            ],
            'content_by_type': [
                {'type': item[0], 'count': item[1]} for item in content_by_type
            ],
            'content_by_genre': [
                {'genre': item[0], 'count': item[1]} for item in content_by_genre
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get analytics', 'error': str(e)}), 500

# Bulk operations
@admin_bp.route('/content/bulk-update', methods=['POST'])
@token_required
@admin_required
def bulk_update_content(current_user):
    try:
        data = request.get_json()
        
        if not data or 'content_ids' not in data or 'action' not in data:
            return jsonify({'message': 'content_ids and action are required'}), 400
        
        content_ids = data['content_ids']
        action = data['action']
        
        if action not in ['activate', 'deactivate', 'feature', 'unfeature']:
            return jsonify({'message': 'Invalid action'}), 400
        
        content_list = Content.query.filter(Content.id.in_(content_ids)).all()
        
        for content in content_list:
            if action == 'activate':
                content.is_active = True
            elif action == 'deactivate':
                content.is_active = False
            elif action == 'feature':
                content.is_featured = True
            elif action == 'unfeature':
                content.is_featured = False
            
            content.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': f'Bulk {action} completed successfully',
            'updated_count': len(content_list)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Bulk update failed', 'error': str(e)}), 500

