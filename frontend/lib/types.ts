export interface ServerlessFunction {
  name: string;
  route: string;
  language: string;
  timeout: number;
  code: string;
  url?: string;
}

export interface AuthResponse {
  access_token: string;
  username: string;
}