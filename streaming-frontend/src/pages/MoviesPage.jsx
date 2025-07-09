import React, { useState, useEffect } from 'react';
import { apiClient } from '../lib/api';

const MoviesPage = () => {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMovies();
  }, []);

  const loadMovies = async () => {
    try {
      const response = await apiClient.getContent({ type: 'movie', per_page: 20 });
      setMovies(response.content || []);
    } catch (error) {
      console.error('Failed to load movies:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Movies</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {movies.map((movie) => (
          <div key={movie.id} className="bg-card rounded-lg overflow-hidden">
            <img
              src={movie.cover_image || '/placeholder-image.jpg'}
              alt={movie.title}
              className="w-full aspect-[2/3] object-cover"
            />
            <div className="p-3">
              <h3 className="font-medium text-sm line-clamp-2">{movie.title}</h3>
              <p className="text-xs text-muted-foreground">{movie.release_year}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MoviesPage;

