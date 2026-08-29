import { api } from "./api";
import type { User } from "../types";

export interface SignupPayload {
  name: string;
  email: string;
  password: string;
  confirm_password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export async function signup(payload: SignupPayload): Promise<string> {
  const { data } = await api.post<{ access_token: string }>("/auth/signup", payload);
  return data.access_token;
}

export async function login(payload: LoginPayload): Promise<string> {
  const { data } = await api.post<{ access_token: string }>("/auth/login", payload);
  return data.access_token;
}

export async function me(): Promise<User> {
  const { data } = await api.get<User>("/auth/me");
  return data;
}

