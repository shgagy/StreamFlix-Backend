import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  BarChart3, 
  Users, 
  Film, 
  Tv, 
  Plus, 
  Settings, 
  Eye,
  Star,
  Calendar,
  TrendingUp,
  Activity,
  Database
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiClient } from '../../lib/api';

const AdminDashboard = () => {
  const location = useLocation();
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalContent: 0,
    totalViews: 0,
    activeUsers: 0,
    topContent: [],
    recentUsers: [],
    contentByGenre: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsResponse, contentResponse, usersResponse] = await Promise.all([
        apiClient.getAdminStats(),
        apiClient.getContent({ per_page: 10, sort_by: 'view_count', order: 'desc' }),
        apiClient.getUsers({ per_page: 10, sort_by: 'created_at', order: 'desc' })
      ]);

      setStats({
        totalUsers: statsResponse.total_users || 0,
        totalContent: statsResponse.total_content || 0,
        totalViews: statsResponse.total_views || 0,
        activeUsers: statsResponse.active_users || 0,
        topContent: contentResponse.content || [],
        recentUsers: usersResponse.users || [],
        contentByGenre: statsResponse.content_by_genre || []
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      // Set mock data for demo
      setStats({
        totalUsers: 1247,
        totalContent: 6,
        totalViews: 45892,
        activeUsers: 89,
        topContent: [],
        recentUsers: [],
        contentByGenre: [
          { name: 'Action', count: 2 },
          { name: 'Drama', count: 3 },
          { name: 'Sci-Fi', count: 1 }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, description, icon: Icon, trend }) => (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value.toLocaleString()}</div>
        <p className="text-xs text-muted-foreground">
          {trend && (
            <span className={`inline-flex items-center ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
              <TrendingUp className="h-3 w-3 mr-1" />
              {trend > 0 ? '+' : ''}{trend}%
            </span>
          )}
          {description}
        </p>
      </CardContent>
    </Card>
  );

  const ContentManagement = () => {
    const [content, setContent] = useState([]);
    const [contentLoading, setContentLoading] = useState(true);

    useEffect(() => {
      loadContent();
    }, []);

    const loadContent = async () => {
      try {
        const response = await apiClient.getContent({ per_page: 20 });
        setContent(response.content || []);
      } catch (error) {
        console.error('Failed to load content:', error);
      } finally {
        setContentLoading(false);
      }
    };

    const toggleContentStatus = async (contentId, isActive) => {
      try {
        await apiClient.updateContent(contentId, { is_active: !isActive });
        loadContent(); // Reload content
      } catch (error) {
        console.error('Failed to update content status:', error);
      }
    };

    if (contentLoading) {
      return <div className="flex items-center justify-center p-8">Loading content...</div>;
    }

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Content Management</h2>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Content
          </Button>
        </div>

        <div className="grid gap-4">
          {content.map((item) => (
            <Card key={item.id}>
              <CardContent className="p-4">
                <div className="flex items-center space-x-4">
                  <img
                    src={item.cover_image || '/placeholder-image.jpg'}
                    alt={item.title}
                    className="w-16 h-24 object-cover rounded"
                  />
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="font-semibold">{item.title}</h3>
                      <Badge variant={item.content_type === 'movie' ? 'default' : 'secondary'}>
                        {item.content_type}
                      </Badge>
                      <Badge variant={item.is_active ? 'default' : 'destructive'}>
                        {item.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
                      {item.description}
                    </p>
                    <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                      <span className="flex items-center">
                        <Calendar className="mr-1 h-3 w-3" />
                        {item.release_year}
                      </span>
                      <span className="flex items-center">
                        <Eye className="mr-1 h-3 w-3" />
                        {item.view_count?.toLocaleString() || 0} views
                      </span>
                      <span className="flex items-center">
                        <Star className="mr-1 h-3 w-3" />
                        {item.rating?.toFixed(1) || 'N/A'}
                      </span>
                    </div>
                  </div>
                  <div className="flex flex-col space-y-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => toggleContentStatus(item.id, item.is_active)}
                    >
                      {item.is_active ? 'Deactivate' : 'Activate'}
                    </Button>
                    <Button variant="outline" size="sm">
                      Edit
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  };

  const UserManagement = () => {
    const [users, setUsers] = useState([]);
    const [usersLoading, setUsersLoading] = useState(true);

    useEffect(() => {
      loadUsers();
    }, []);

    const loadUsers = async () => {
      try {
        const response = await apiClient.getUsers({ per_page: 20 });
        setUsers(response.users || []);
      } catch (error) {
        console.error('Failed to load users:', error);
        // Mock data for demo
        setUsers([
          {
            id: 1,
            username: 'admin',
            email: 'admin@streamflix.com',
            is_admin: true,
            is_active: true,
            created_at: '2025-01-01T00:00:00Z'
          },
          {
            id: 2,
            username: 'john_doe',
            email: 'john@example.com',
            is_admin: false,
            is_active: true,
            created_at: '2025-01-02T00:00:00Z'
          }
        ]);
      } finally {
        setUsersLoading(false);
      }
    };

    if (usersLoading) {
      return <div className="flex items-center justify-center p-8">Loading users...</div>;
    }

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">User Management</h2>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add User
          </Button>
        </div>

        <div className="grid gap-4">
          {users.map((user) => (
            <Card key={user.id}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="font-semibold">{user.username}</h3>
                      {user.is_admin && (
                        <Badge variant="destructive">Admin</Badge>
                      )}
                      <Badge variant={user.is_active ? 'default' : 'secondary'}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{user.email}</p>
                    <p className="text-xs text-muted-foreground">
                      Joined {new Date(user.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm">
                      Edit
                    </Button>
                    <Button 
                      variant={user.is_active ? "destructive" : "default"} 
                      size="sm"
                    >
                      {user.is_active ? 'Deactivate' : 'Activate'}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
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
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Admin Dashboard</h1>
        <p className="text-muted-foreground">
          Manage your streaming platform content, users, and analytics
        </p>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="content">Content</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Stats Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Users"
              value={stats.totalUsers}
              description="from last month"
              icon={Users}
              trend={12}
            />
            <StatCard
              title="Total Content"
              value={stats.totalContent}
              description="movies & series"
              icon={Database}
            />
            <StatCard
              title="Total Views"
              value={stats.totalViews}
              description="this month"
              icon={Eye}
              trend={8}
            />
            <StatCard
              title="Active Users"
              value={stats.activeUsers}
              description="last 24 hours"
              icon={Activity}
              trend={-2}
            />
          </div>

          {/* Charts and Recent Activity */}
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Content by Genre</CardTitle>
                <CardDescription>Distribution of content across genres</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {stats.contentByGenre.map((genre, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{genre.name}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-primary rounded-full"
                            style={{ 
                              width: `${(genre.count / Math.max(...stats.contentByGenre.map(g => g.count))) * 100}%` 
                            }}
                          />
                        </div>
                        <span className="text-sm text-muted-foreground">{genre.count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Common administrative tasks</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full justify-start">
                  <Plus className="mr-2 h-4 w-4" />
                  Add New Movie
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  <Tv className="mr-2 h-4 w-4" />
                  Add New Series
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  <Users className="mr-2 h-4 w-4" />
                  Manage Users
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  <Settings className="mr-2 h-4 w-4" />
                  Platform Settings
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="content">
          <ContentManagement />
        </TabsContent>

        <TabsContent value="users">
          <UserManagement />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminDashboard;

