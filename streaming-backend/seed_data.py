#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models.user import User, db
from src.models.content import Content, Episode, Genre
from src.models.interactions import Rating, Comment, WatchHistory, Favorite
from datetime import datetime, date

def seed_database():
    # Configure database for seeding, prioritizing DATABASE_URL
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///database/app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        print("Seeding database with sample data...")
        
        # Create genres
        genres_data = [
            {'name': 'Action', 'description': 'High-energy films with exciting sequences'},
            {'name': 'Drama', 'description': 'Character-driven stories with emotional depth'},
            {'name': 'Comedy', 'description': 'Light-hearted entertainment designed to amuse'},
            {'name': 'Thriller', 'description': 'Suspenseful stories that keep you on edge'},
            {'name': 'Horror', 'description': 'Scary movies designed to frighten and thrill'},
            {'name': 'Romance', 'description': 'Love stories and romantic relationships'},
            {'name': 'Sci-Fi', 'description': 'Science fiction and futuristic themes'},
            {'name': 'Fantasy', 'description': 'Magical and supernatural elements'},
            {'name': 'Crime', 'description': 'Stories involving criminal activities'},
            {'name': 'Documentary', 'description': 'Non-fiction films about real subjects'}
        ]
        
        genres = []
        for genre_data in genres_data:
            genre = Genre(**genre_data)
            db.session.add(genre)
            genres.append(genre)
        
        db.session.commit()
        print(f"Created {len(genres)} genres")
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@streamingplatform.com',
            is_admin=True
        )
        admin.set_password('Admin123!')
        db.session.add(admin)
        
        # Create regular users
        users_data = [
            {'username': 'john_doe', 'email': 'john@example.com', 'password': 'Password123!'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'password': 'Password123!'},
            {'username': 'movie_lover', 'email': 'lover@example.com', 'password': 'Password123!'},
            {'username': 'series_fan', 'email': 'fan@example.com', 'password': 'Password123!'}
        ]
        
        users = [admin]
        for user_data in users_data:
            user = User(
                username=user_data['username'],
                email=user_data['email']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            users.append(user)
        
        db.session.commit()
        print(f"Created {len(users)} users")
        
        # Create sample movies
        movies_data = [
            {
                'title': 'The Dark Knight',
                'description': 'Batman faces the Joker in this epic superhero thriller.',
                'content_type': 'movie',
                'cover_image': 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg',
                'release_year': 2008,
                'duration': 152,
                'imdb_rating': 9.0,
                'language': 'English',
                'country': 'USA',
                'director': 'Christopher Nolan',
                'cast': 'Christian Bale, Heath Ledger, Aaron Eckhart',
                'is_featured': True,
                'video_url': 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4',
                'genre_names': ['Action', 'Crime', 'Drama']
            },
            {
                'title': 'Inception',
                'description': 'A thief enters people\'s dreams to steal secrets.',
                'content_type': 'movie',
                'cover_image': 'https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg',
                'release_year': 2010,
                'duration': 148,
                'imdb_rating': 8.8,
                'language': 'English',
                'country': 'USA',
                'director': 'Christopher Nolan',
                'cast': 'Leonardo DiCaprio, Marion Cotillard, Tom Hardy',
                'is_featured': True,
                'video_url': 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_2mb.mp4',
                'genre_names': ['Sci-Fi', 'Action', 'Thriller']
            },
            {
                'title': 'The Shawshank Redemption',
                'description': 'Two imprisoned men bond over years, finding solace and redemption.',
                'content_type': 'movie',
                'cover_image': 'https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg',
                'release_year': 1994,
                'duration': 142,
                'imdb_rating': 9.3,
                'language': 'English',
                'country': 'USA',
                'director': 'Frank Darabont',
                'cast': 'Tim Robbins, Morgan Freeman, Bob Gunton',
                'is_featured': False,
                'video_url': 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_5mb.mp4',
                'genre_names': ['Drama']
            },
            {
                'title': 'Pulp Fiction',
                'description': 'The lives of two mob hitmen, a boxer, and others intertwine.',
                'content_type': 'movie',
                'cover_image': 'https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg',
                'release_year': 1994,
                'duration': 154,
                'imdb_rating': 8.9,
                'language': 'English',
                'country': 'USA',
                'director': 'Quentin Tarantino',
                'cast': 'John Travolta, Uma Thurman, Samuel L. Jackson',
                'is_featured': False,
                'video_url': 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4',
                'genre_names': ['Crime', 'Drama']
            }
        ]
        
        movies = []
        for movie_data in movies_data:
            genre_names = movie_data.pop('genre_names', [])
            movie = Content(**movie_data)
            
            # Add genres
            movie_genres = [g for g in genres if g.name in genre_names]
            movie.genres = movie_genres
            
            db.session.add(movie)
            movies.append(movie)
        
        # Create sample series
        series_data = [
            {
                'title': 'Breaking Bad',
                'description': 'A high school chemistry teacher turned methamphetamine manufacturer.',
                'content_type': 'series',
                'cover_image': 'https://image.tmdb.org/t/p/w500/ggFHVNu6YYI5L9pCfOacjizRGt.jpg',
                'release_year': 2008,
                'imdb_rating': 9.5,
                'language': 'English',
                'country': 'USA',
                'director': 'Vince Gilligan',
                'cast': 'Bryan Cranston, Aaron Paul, Anna Gunn',
                'is_featured': True,
                'genre_names': ['Drama', 'Crime', 'Thriller']
            },
            {
                'title': 'Stranger Things',
                'description': 'Kids in a small town uncover supernatural mysteries.',
                'content_type': 'series',
                'cover_image': 'https://image.tmdb.org/t/p/w500/49WJfeN0moxb9IPfGn8AIqMGskD.jpg',
                'release_year': 2016,
                'imdb_rating': 8.7,
                'language': 'English',
                'country': 'USA',
                'director': 'The Duffer Brothers',
                'cast': 'Millie Bobby Brown, Finn Wolfhard, Winona Ryder',
                'is_featured': True,
                'genre_names': ['Sci-Fi', 'Horror', 'Drama']
            }
        ]
        
        series = []
        for series_data in series_data:
            genre_names = series_data.pop('genre_names', [])
            show = Content(**series_data)
            
            # Add genres
            show_genres = [g for g in genres if g.name in genre_names]
            show.genres = show_genres
            
            db.session.add(show)
            series.append(show)
        
        db.session.commit()
        print(f"Created {len(movies)} movies and {len(series)} series")
        
        # Create episodes for series
        episodes_data = [
            # Breaking Bad Season 1
            {
                'series_title': 'Breaking Bad',
                'title': 'Pilot',
                'description': 'Walter White, a struggling high school chemistry teacher, is diagnosed with lung cancer.',
                'episode_number': 1,
                'season_number': 1,
                'duration': 58,
                'video_url': 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4',
                'air_date': date(2008, 1, 20)
            },
            {
                'series_title': 'Breaking Bad',
                'title': 'Cat\'s in the Bag...',
                'description': 'Walt and Jesse attempt to tie up loose ends.',
                'episode_number': 2,
                'season_number': 1,
                'duration': 48,
                'video_url': 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_2mb.mp4',
                'air_date': date(2008, 1, 27)
            },
            # Stranger Things Season 1
            {
                'series_title': 'Stranger Things',
                'title': 'Chapter One: The Vanishing of Will Byers',
                'description': 'A young boy vanishes on his way home from a friend\'s house.',
                'episode_number': 1,
                'season_number': 1,
                'duration': 47,
                'video_url': 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4',
                'air_date': date(2016, 7, 15)
            },
            {
                'series_title': 'Stranger Things',
                'title': 'Chapter Two: The Weirdo on Maple Street',
                'description': 'Lucas, Mike and Dustin try to talk to the girl they found in the woods.',
                'episode_number': 2,
                'season_number': 1,
                'duration': 55,
                'video_url': 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_2mb.mp4',
                'air_date': date(2016, 7, 15)
            }
        ]
        
        episodes = []
        for episode_data in episodes_data:
            series_title = episode_data.pop('series_title')
            show = next((s for s in series if s.title == series_title), None)
            if show:
                episode = Episode(series_id=show.id, **episode_data)
                db.session.add(episode)
                episodes.append(episode)
        
        db.session.commit()
        print(f"Created {len(episodes)} episodes")
        
        # Create sample ratings and comments
        import random
        
        all_content = movies + series
        regular_users = users[1:]  # Exclude admin
        
        # Add ratings
        for content in all_content:
            for user in random.sample(regular_users, random.randint(1, 3)):
                rating = Rating(
                    user_id=user.id,
                    content_id=content.id,
                    score=random.uniform(6.0, 10.0)
                )
                db.session.add(rating)
        
        # Add comments
        comments_text = [
            "Amazing movie! Loved every minute of it.",
            "Great acting and storyline.",
            "One of the best I've ever seen.",
            "Highly recommended!",
            "The cinematography is outstanding.",
            "A masterpiece of modern cinema.",
            "Couldn't stop watching!",
            "Brilliant writing and direction."
        ]
        
        for content in all_content:
            for user in random.sample(regular_users, random.randint(0, 2)):
                comment = Comment(
                    user_id=user.id,
                    content_id=content.id,
                    text=random.choice(comments_text)
                )
                db.session.add(comment)
        
        # Add some watch history
        for user in regular_users:
            for content in random.sample(all_content, random.randint(1, 3)):
                watch_history = WatchHistory(
                    user_id=user.id,
                    content_id=content.id,
                    watch_time=random.randint(300, 7200),  # 5 minutes to 2 hours
                    total_time=content.duration * 60 if content.duration else 7200,
                    completed=random.choice([True, False])
                )
                db.session.add(watch_history)
        
        # Add some favorites
        for user in regular_users:
            for content in random.sample(all_content, random.randint(0, 2)):
                favorite = Favorite(
                    user_id=user.id,
                    content_id=content.id
                )
                db.session.add(favorite)
        
        db.session.commit()
        
        # Update content ratings
        for content in all_content:
            content.calculate_average_rating()
        
        # Add some view counts
        for content in all_content:
            content.view_count = random.randint(100, 10000)
        
        db.session.commit()
        
        print("Database seeded successfully!")
        print("\nSample login credentials:")
        print("Admin: admin / Admin123!")
        print("User: john_doe / Password123!")
        print("User: jane_smith / Password123!")

if __name__ == '__main__':
    seed_database()


