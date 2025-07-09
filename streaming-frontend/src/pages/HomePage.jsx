import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Play, Info, Star, Calendar, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { apiClient } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

const HomePage = () => {
  const { isAuthenticated } = useAuth();
  const [featuredContent, setFeaturedContent] = useState([]);
  const [latestMovies, setLatestMovies] = useState([]);
  const [latestSeries, setLatestSeries] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHomeData();
  }, [isAuthenticated]);

  const loadHomeData = async () => {
    try {
      setLoading(true);

      // Load featured content
      const featuredResponse = await apiClient.getContent({
        featured: true,
        per_page: 5,
        sort_by: 'view_count',
        order: 'desc'
      });
      setFeaturedContent(featuredResponse.content || []);

      // Load latest movies
      const moviesResponse = await apiClient.getContent({
        type: 'movie',
        per_page: 8,
        sort_by: 'created_at',
        order: 'desc'
      });
      setLatestMovies(moviesResponse.content || []);

      // Load latest series
      const seriesResponse = await apiClient.getContent({
        type: 'series',
        per_page: 8,
        sort_by: 'created_at',
        order: 'desc'
      });
      setLatestSeries(seriesResponse.content || []);

      // Load recommendations if authenticated
      if (isAuthenticated) {
        try {
          const recommendationsResponse = await apiClient.getRecommendations();
          setRecommendations(recommendationsResponse || []);
        } catch (error) {
          console.error('Failed to load recommendations:', error);
        }
      }
    } catch (error) {
      console.error('Failed to load home data:', error);
    } finally {
      setLoading(false);
    }
  };

  const HeroSection = ({ content }) => {
    if (!content || content.length === 0) return null;

    const heroItem = content[0];

    return (
      <section className="relative h-[70vh] min-h-[500px] overflow-hidden">
        <div className="absolute inset-0">
          <img
            src={heroItem.cover_image || '/placeholder-image.jpg'}
            alt={heroItem.title}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/40 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
        </div>

        <div className="relative z-10 container mx-auto px-4 h-full flex items-center">
          <div className="max-w-2xl">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
              {heroItem.title}
            </h1>
            
            <div className="flex items-center space-x-4 mb-4">
              <div className="flex items-center space-x-1">
                <Star className="h-4 w-4 text-yellow-400 fill-current" />
                <span className="text-white font-medium">
                  {heroItem.rating?.toFixed(1) || 'N/A'}
                </span>
              </div>
              <Badge variant="secondary">{heroItem.content_type}</Badge>
              {heroItem.release_year && (
                <div className="flex items-center space-x-1 text-white">
                  <Calendar className="h-4 w-4" />
                  <span>{heroItem.release_year}</span>
                </div>
              )}
              {heroItem.duration && (
                <div className="flex items-center space-x-1 text-white">
                  <Clock className="h-4 w-4" />
                  <span>{heroItem.duration}m</span>
                </div>
              )}
            </div>

            <p className="text-lg text-gray-200 mb-8 line-clamp-3">
              {heroItem.description}
            </p>

            <div className="flex items-center space-x-4">
              <Button size="lg" asChild>
                <Link to={`/content/${heroItem.id}`}>
                  <Play className="mr-2 h-5 w-5" />
                  Watch Now
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link to={`/content/${heroItem.id}`}>
                  <Info className="mr-2 h-5 w-5" />
                  More Info
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    );
  };

  const ContentRow = ({ title, content, viewAllLink }) => {
    if (!content || content.length === 0) return null;

    return (
      <section className="py-8">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">{title}</h2>
            {viewAllLink && (
              <Button variant="ghost" asChild>
                <Link to={viewAllLink}>View All</Link>
              </Button>
            )}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
            {content.map((item) => (
              <ContentCard key={item.id} content={item} />
            ))}
          </div>
        </div>
      </section>
    );
  };

  const ContentCard = ({ content }) => {
    return (
      <Link to={`/content/${content.id}`} className="group">
        <Card className="overflow-hidden transition-transform hover:scale-105">
          <CardContent className="p-0">
            <div className="aspect-[2/3] relative overflow-hidden">
              <img
                src={content.cover_image || '/placeholder-image.jpg'}
                alt={content.title}
                className="w-full h-full object-cover transition-transform group-hover:scale-110"
              />
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors" />
              <div className="absolute top-2 right-2">
                <Badge variant="secondary" className="text-xs">
                  {content.content_type}
                </Badge>
              </div>
              {content.rating && (
                <div className="absolute bottom-2 left-2 flex items-center space-x-1 bg-black/70 rounded px-2 py-1">
                  <Star className="h-3 w-3 text-yellow-400 fill-current" />
                  <span className="text-white text-xs font-medium">
                    {content.rating.toFixed(1)}
                  </span>
                </div>
              )}
            </div>
            <div className="p-3">
              <h3 className="font-medium text-sm line-clamp-2 mb-1">
                {content.title}
              </h3>
              <p className="text-xs text-muted-foreground">
                {content.release_year}
              </p>
            </div>
          </CardContent>
        </Card>
      </Link>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <HeroSection content={featuredContent} />
      
      {isAuthenticated && recommendations.length > 0 && (
        <ContentRow
          title="Recommended for You"
          content={recommendations}
        />
      )}

      <ContentRow
        title="Latest Movies"
        content={latestMovies}
        viewAllLink="/movies"
      />

      <ContentRow
        title="Latest TV Series"
        content={latestSeries}
        viewAllLink="/series"
      />

      {featuredContent.length > 1 && (
        <ContentRow
          title="Featured Content"
          content={featuredContent.slice(1)}
        />
      )}
    </div>
  );
};

export default HomePage;

