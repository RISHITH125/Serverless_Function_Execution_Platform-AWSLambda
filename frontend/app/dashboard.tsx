'use client';

import { useState, useEffect } from 'react';
import { useAuth } from './auth-provider';
import { getFunctions, createFunction, updateFunction, deleteFunction } from '@/lib/api';
import type { ServerlessFunction } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import { Trash2, Edit, Plus } from 'lucide-react';

export default function Dashboard() {
  const { token, setToken } = useAuth();
  const [functions, setFunctions] = useState<ServerlessFunction[]>([]);
  const [selectedFunction, setSelectedFunction] = useState<ServerlessFunction | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    if (token) {
      loadFunctions();
    }
  }, [token]);

  const loadFunctions = async () => {
    try {
      const data = await getFunctions(token!);
      setFunctions(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load functions",
        variant: "destructive",
      });
    }
  };

  const handleSubmit = async (func: ServerlessFunction, isEdit: boolean) => {
    try {
      if (isEdit) {
        await updateFunction(token!, func.name, func);
      } else {
        await createFunction(token!, func);
      }
      loadFunctions();
      toast({
        title: `Function ${isEdit ? 'updated' : 'created'} successfully`,
        description: `${func.name} has been ${isEdit ? 'updated' : 'created'}.`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to ${isEdit ? 'update' : 'create'} function`,
        variant: "destructive",
      });
    }
  };

  const handleDelete = async (name: string) => {
    try {
      await deleteFunction(token!, name);
      loadFunctions();
      toast({
        title: "Function deleted",
        description: `${name} has been deleted.`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete function",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Serverless Functions</h1>
          <div className="space-x-4">
            <Dialog>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  New Function
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create New Function</DialogTitle>
                </DialogHeader>
                <FunctionForm onSubmit={(func) => handleSubmit(func, false)} />
              </DialogContent>
            </Dialog>
            <Button variant="outline" onClick={() => {
              setToken(null)
              localStorage.removeItem("cc-serverless-accesstoken");
            }}>
              Logout
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {functions.map((func) => (
            <Card key={func.name}>
              <CardHeader>
                <CardTitle className="flex justify-between items-center">
                  <span>{func.name}</span>
                  <div className="space-x-2">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <Edit className="h-4 w-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Edit Function</DialogTitle>
                        </DialogHeader>
                        <FunctionForm 
                          initialData={func}
                          onSubmit={(updatedFunc) => handleSubmit(updatedFunc, true)} 
                        />
                      </DialogContent>
                    </Dialog>
                    <Button 
                      variant="ghost" 
                      size="icon"
                      onClick={() => handleDelete(func.name)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p><strong>Route:</strong> {func.route}</p>
                  <p><strong>Language:</strong> {func.language}</p>
                  <p><strong>Timeout:</strong> {func.timeout}ms</p>
                  <div className="mt-4">
                    <p className="font-semibold mb-2">Code:</p>
                    <pre className="bg-muted p-2 rounded-md overflow-x-auto">
                      <code>{func.code}</code>
                    </pre>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}

function FunctionForm({ 
  initialData,
  onSubmit 
}: { 
  initialData?: ServerlessFunction;
  onSubmit: (func: ServerlessFunction) => void;
}) {
  const [formData, setFormData] = useState<ServerlessFunction>(
    initialData || {
      name: '',
      route: '',
      language: 'javascript',
      timeout: 1000,
      code: '',
    }
  );

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <label className="text-sm font-medium">Name</label>
        <Input
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          disabled={!!initialData}
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium">Route</label>
        <Input
          value={formData.route}
          onChange={(e) => setFormData({ ...formData, route: e.target.value })}
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium">Language</label>
        <Input
          value={formData.language}
          onChange={(e) => setFormData({ ...formData, language: e.target.value })}
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium">Timeout (ms)</label>
        <Input
          type="number"
          value={formData.timeout}
          onChange={(e) => setFormData({ ...formData, timeout: parseInt(e.target.value) })}
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium">Code</label>
        <Textarea
          value={formData.code}
          onChange={(e) => setFormData({ ...formData, code: e.target.value })}
          className="font-mono"
          rows={6}
        />
      </div>
      <Button className="w-full" onClick={() => onSubmit(formData)}>
        {initialData ? 'Update' : 'Create'} Function
      </Button>
    </div>
  );
}