import { AuthResponse, ServerlessFunction } from "./types";

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function signup(username: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  
  if (!response.ok) throw new Error('Signup failed');
  return response.json();
}

export async function login(username: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  
  if (!response.ok) throw new Error('Login failed');
  return response.json();
}

export async function getFunctions(token: string): Promise<ServerlessFunction[]> {
  const response = await fetch(`${API_URL}/functions`, {
    headers: { 
      'Authorization': `Bearer ${token}`,
    },
  });
  
  if (!response.ok) throw new Error('Failed to fetch functions');
  return response.json();
}

export async function getFunction(token: string, name: string): Promise<ServerlessFunction> {
  const response = await fetch(`${API_URL}/function/${name}`, {
    headers: { 
      'Authorization': `Bearer ${token}`,
    },
  });
  
  if (!response.ok) throw new Error('Failed to fetch function');
  return response.json();
}

export async function createFunction(token: string, func: ServerlessFunction): Promise<void> {
  const response = await fetch(`${API_URL}/function`, {
    method: 'POST',
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(func),
  });
  
  if (!response.ok) throw new Error('Failed to create function');
}

export async function updateFunction(token: string, name: string, func: ServerlessFunction): Promise<void> {
  const response = await fetch(`${API_URL}/function/${name}`, {
    method: 'PUT',
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(func),
  });
  
  if (!response.ok) throw new Error('Failed to update function');
}

export async function deleteFunction(token: string, name: string): Promise<void> {
  const response = await fetch(`${API_URL}/function/${name}`, {
    method: 'DELETE',
    headers: { 
      'Authorization': `Bearer ${token}`,
    },
  });
  
  if (!response.ok) throw new Error('Failed to delete function');
}
