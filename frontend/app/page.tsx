'use client';

import { useEffect, useState } from 'react';
import { useAuth } from './auth-provider';
import { login, signup } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Dashboard from './dashboard';

export default function Home() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { token, setToken } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    if (localStorage && localStorage.getItem("cc-serverless-accesstoken")) {
      setToken(localStorage.getItem("cc-serverless-accesstoken"))
    }
  }, [])

  const handleAuth = async (type: 'login' | 'signup') => {
    try {
      const authFn = type === 'login' ? login : signup;
      const response = await authFn(username, password);
      setToken(response.access_token);
      localStorage.setItem("cc-serverless-username", response.username)
      localStorage.setItem("cc-serverless-accesstoken", response.access_token)
      toast({
        title: `${type === 'login' ? 'Logged in' : 'Signed up'} successfully`,
        description: "Welcome to the Serverless Functions Interface",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to ${type}. Please try again.`,
        variant: "destructive",
      });
    }
  };

  if (token) {
    return <Dashboard />;
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl text-center">
            Serverless Functions Interface
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="login">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="signup">Sign Up</TabsTrigger>
            </TabsList>
            <TabsContent value="login" className="space-y-4">
              <div className="space-y-2">
                <Input
                  placeholder="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
                <Input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <Button 
                  className="w-full" 
                  onClick={() => handleAuth('login')}
                >
                  Login
                </Button>
              </div>
            </TabsContent>
            <TabsContent value="signup" className="space-y-4">
              <div className="space-y-2">
                <Input
                  placeholder="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
                <Input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <Button 
                  className="w-full" 
                  onClick={() => handleAuth('signup')}
                >
                  Sign Up
                </Button>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}