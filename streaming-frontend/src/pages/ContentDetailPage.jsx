import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Play, 
  Plus, 
  Heart, 
  Star, 
  Calendar, 
  Clock, 
  Users, 
  Globe,
  Film,
  Tv,
  MessageCircle,
  ThumbsUp,
  Share2,
  Download,
  Settings
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiClient } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

const ContentDetailPage = () => {
  const { id } = useParams();
  const { isAuthenticated } = useAuth();
  const [content, setContent] = useState(null);
  const [episodes, setEpisodes] = useState([]);
  const [comments, setComments] = useState([]);
  const [userRating, setUserRating] = useState(0);
  const [isFavorite, setIsFavorite] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selectedSeason, setSelectedSeason] = useState(1);

  useEffect(() => {
    if (id) {
      loadContentDetail();
    }
  }, [id]);

  const loadContentDetail = async () => {
    try {
      setLoading(true);
      
      // Load content details
      const contentResponse = await apiClient.getContentDetail(id);
      setContent(contentResponse);

      // Load episodes if it's a series
      if (contentResponse.content_type === 'series') {
        try {
          const episodesResponse = await apiClient.getEpisodes(id, selectedSeason);
          setEpisodes(episodesResponse.episodes || []);
        } catch (error) {
          console.error('Failed to load episodes:', error);
        }
      }

      // Load comments
      try {
        const commentsResponse = await apiClient.getComments(id);
        setComments(commentsResponse.comments || []);
      } catch (error) {
        console.error('Failed to load comments:', error);
      }

      // Load user-specific data if authenticated
      if (isAuthenticated) {
        try {
          const ratingResponse = await apiClient.getUserRating(id);
          setUserRating(ratingResponse.score || 0);
        } catch (error) {
          console.error('Failed to load user rating:', error);
        }

        try {
          const favoriteResponse = await apiClient.checkFavorite(id);
          setIsFavorite(favoriteResponse.is_favorite || false);
        } catch (error) {
          console.error('Failed to check favorite status:', error);
        }
      }
    } catch (error) {
      console.error('Failed to load content detail:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRating = async (score) => {
    if (!isAuthenticated) return;
    
    try {
      await apiClient.rateContent(id, score);
      setUserRating(score);
      // Reload content to get updated average rating
      loadContentDetail();
    } catch (error) {
      console.error('Failed to rate content:', error);
    }
  };

  const toggleFavorite = async () => {
    if (!isAuthenticated) return;

    try {
      if (isFavorite) {
        await apiClient.removeFromFavorites(id);
        setIsFavorite(false);
      } else {
        await apiClient.addToFavorites(id);
        setIsFavorite(true);
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  const handleWatchNow = async () => {
    if (!isAuthenticated) return;

    try {
      // Update watch history
      await apiClient.updateWatchHistory({
        content_id: parseInt(id),
        progress: 0,
        completed: false
      });
    } catch (error) {
      console.error('Failed to update watch history:', error);
    }
  };

  const StarRating = ({ rating, onRate, interactive = false }) => {
    return (
      <div className="flex items-center space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onClick={() => interactive && onRate && onRate(star)}
            className={`${interactive ? 'cursor-pointer hover:scale-110' : 'cursor-default'} transition-transform`}
            disabled={!interactive}
          >
            <Star
              className={`h-5 w-5 ${
                star <= rating
                  ? 'text-yellow-400 fill-current'
                  : 'text-gray-300'
              }`}
            />
          </button>
        ))}
      </div>
    );
  };

  const EpisodeCard = ({ episode }) => (
    <Card className="mb-4">
      <CardContent className="p-4">
        <div className="flex items-start space-x-4">
          <div className="w-32 h-20 bg-muted rounded overflow-hidden flex-shrink-0">
            <img
              src={episode.thumbnail || content?.cover_image || '/placeholder-image.jpg'}
              alt={episode.title}
              className="w-full h-full object-cover"
            />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-semibold">
                {episode.episode_number}. {episode.title}
              </h4>
              <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                <Clock className="h-4 w-4" />
                <span>{episode.duration}m</span>
              </div>
            </div>
            <p className="text-sm text-muted-foreground line-clamp-2">
              {episode.description}
            </p>
          </div>
          <Button size="sm" onClick={handleWatchNow}>
            <Play className="h-4 w-4 mr-1" />
            Play
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  const CommentCard = ({ comment }) => (
    <Card className="mb-4">
      <CardContent className="p-4">
        <div className="flex items-start space-x-3">
          <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground text-sm font-medium">
            {comment.user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-1">
              <span className="font-medium text-sm">{comment.user?.username || 'Anonymous'}</span>
              <span className="text-xs text-muted-foreground">
                {new Date(comment.created_at).toLocaleDateString()}
              </span>
            </div>
            <p className="text-sm">{comment.text}</p>
            <div className="flex items-center space-x-4 mt-2">
              <Button variant="ghost" size="sm">
                <ThumbsUp className="h-4 w-4 mr-1" />
                Like
              </Button>
              <Button variant="ghost" size="sm">
                <MessageCircle className="h-4 w-4 mr-1" />
                Reply
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!content) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Content Not Found</h1>
          <p className="text-muted-foreground mb-4">The content you're looking for doesn't exist.</p>
          <Button asChild>
            <Link to="/">Go Home</Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative h-[60vh] min-h-[400px] overflow-hidden">
        <div className="absolute inset-0">
          <img
            src={content.cover_image || '/placeholder-image.jpg'}
            alt={content.title}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/40 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
        </div>

        <div className="relative z-10 container mx-auto px-4 h-full flex items-end pb-8">
          <div className="max-w-2xl">
            <div className="flex items-center space-x-2 mb-4">
              <Badge variant="secondary" className="text-sm">
                {content.content_type === 'movie' ? (
                  <><Film className="h-3 w-3 mr-1" /> Movie</>
                ) : (
                  <><Tv className="h-3 w-3 mr-1" /> Series</>
                )}
              </Badge>
              {content.genres?.map((genre) => (
                <Badge key={genre.id} variant="outline" className="text-sm">
                  {genre.name}
                </Badge>
              ))}
            </div>

            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              {content.title}
            </h1>
            
            <div className="flex items-center space-x-6 mb-4 text-white">
              <div className="flex items-center space-x-1">
                <Star className="h-5 w-5 text-yellow-400 fill-current" />
                <span className="font-medium">{content.rating?.toFixed(1) || 'N/A'}</span>
                <span className="text-sm text-gray-300">({content.imdb_rating || 'N/A'} IMDb)</span>
              </div>
              {content.release_year && (
                <div className="flex items-center space-x-1">
                  <Calendar className="h-4 w-4" />
                  <span>{content.release_year}</span>
                </div>
              )}
              {content.duration && (
                <div className="flex items-center space-x-1">
                  <Clock className="h-4 w-4" />
                  <span>{content.duration}m</span>
                </div>
              )}
              {content.country && (
                <div className="flex items-center space-x-1">
                  <Globe className="h-4 w-4" />
                  <span>{content.country}</span>
                </div>
              )}
            </div>

            <p className="text-lg text-gray-200 mb-6 line-clamp-3">
              {content.description}
            </p>

            <div className="flex items-center space-x-4">
              <Button size="lg" onClick={handleWatchNow}>
                <Play className="mr-2 h-5 w-5" />
                Watch Now
              </Button>
              
              {isAuthenticated && (
                <>
                  <Button variant="outline" size="lg" onClick={toggleFavorite}>
                    <Heart className={`mr-2 h-5 w-5 ${isFavorite ? 'fill-current text-red-500' : ''}`} />
                    {isFavorite ? 'Remove from List' : 'Add to List'}
                  </Button>
                  
                  <Button variant="outline" size="lg">
                    <Share2 className="mr-2 h-5 w-5" />
                    Share
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Content Details */}
      <section className="container mx-auto px-4 py-8">
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <Tabs defaultValue="overview" className="space-y-6">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                {content.content_type === 'series' && (
                  <TabsTrigger value="episodes">Episodes</TabsTrigger>
                )}
                <TabsTrigger value="comments">Comments</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Synopsis</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground leading-relaxed">
                      {content.description}
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Cast & Crew</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {content.director && (
                        <div>
                          <span className="font-medium">Director: </span>
                          <span className="text-muted-foreground">{content.director}</span>
                        </div>
                      )}
                      {content.cast && (
                        <div>
                          <span className="font-medium">Cast: </span>
                          <span className="text-muted-foreground">{content.cast}</span>
                        </div>
                      )}
                      <div>
                        <span className="font-medium">Language: </span>
                        <span className="text-muted-foreground">{content.language || 'English'}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {isAuthenticated && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Rate This {content.content_type === 'movie' ? 'Movie' : 'Series'}</CardTitle>
                      <CardDescription>
                        Share your opinion with other viewers
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center space-x-4">
                        <StarRating 
                          rating={userRating} 
                          onRate={handleRating} 
                          interactive={true}
                        />
                        <span className="text-sm text-muted-foreground">
                          {userRating > 0 ? `You rated this ${userRating}/5` : 'Click to rate'}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              {content.content_type === 'series' && (
                <TabsContent value="episodes" className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xl font-semibold">Episodes</h3>
                    <select 
                      value={selectedSeason}
                      onChange={(e) => setSelectedSeason(parseInt(e.target.value))}
                      className="bg-background border border-border rounded px-3 py-1"
                    >
                      <option value={1}>Season 1</option>
                      <option value={2}>Season 2</option>
                      <option value={3}>Season 3</option>
                    </select>
                  </div>
                  
                  <div className="space-y-4">
                    {episodes.length > 0 ? (
                      episodes.map((episode) => (
                        <EpisodeCard key={episode.id} episode={episode} />
                      ))
                    ) : (
                      <p className="text-muted-foreground text-center py-8">
                        No episodes available for this season.
                      </p>
                    )}
                  </div>
                </TabsContent>
              )}

              <TabsContent value="comments" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Comments ({comments.length})</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {isAuthenticated ? (
                      <div className="mb-6">
                        <textarea
                          placeholder="Write a comment..."
                          className="w-full p-3 border border-border rounded-md bg-background resize-none"
                          rows={3}
                        />
                        <Button className="mt-2">Post Comment</Button>
                      </div>
                    ) : (
                      <div className="mb-6 p-4 bg-muted rounded-md text-center">
                        <p className="text-muted-foreground mb-2">Sign in to leave a comment</p>
                        <Button variant="outline" asChild>
                          <Link to="/login">Sign In</Link>
                        </Button>
                      </div>
                    )}

                    <div className="space-y-4">
                      {comments.length > 0 ? (
                        comments.map((comment) => (
                          <CommentCard key={comment.id} comment={comment} />
                        ))
                      ) : (
                        <p className="text-muted-foreground text-center py-8">
                          No comments yet. Be the first to share your thoughts!
                        </p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <span className="font-medium">Release Year: </span>
                  <span className="text-muted-foreground">{content.release_year}</span>
                </div>
                <div>
                  <span className="font-medium">Views: </span>
                  <span className="text-muted-foreground">{content.view_count?.toLocaleString() || 0}</span>
                </div>
                <div>
                  <span className="font-medium">Rating: </span>
                  <span className="text-muted-foreground">{content.rating?.toFixed(1) || 'N/A'}/10</span>
                </div>
                {content.imdb_rating && (
                  <div>
                    <span className="font-medium">IMDb: </span>
                    <span className="text-muted-foreground">{content.imdb_rating}/10</span>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Genres</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {content.genres?.map((genre) => (
                    <Badge key={genre.id} variant="secondary">
                      {genre.name}
                    </Badge>
                  )) || <span className="text-muted-foreground">No genres available</span>}
                </div>
              </CardContent>
            </Card>

            {isAuthenticated && (
              <Card>
                <CardHeader>
                  <CardTitle>Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button variant="outline" className="w-full justify-start">
                    <Download className="mr-2 h-4 w-4" />
                    Download
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Settings className="mr-2 h-4 w-4" />
                    Quality Settings
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </section>
    </div>
  );
};

export default ContentDetailPage;

