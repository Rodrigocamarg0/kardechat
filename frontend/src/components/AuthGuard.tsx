"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";
import type { Session } from "@supabase/supabase-js";

interface AuthGuardProps {
  children: (session: Session) => React.ReactNode;
}

export default function AuthGuard({ children }: AuthGuardProps) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-spirit-50">
        <div className="text-spirit-600 text-lg">Carregando...</div>
      </div>
    );
  }

  if (!session) {
    return <LoginScreen />;
  }

  return <>{children(session)}</>;
}

function LoginScreen() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback`,
      },
    });

    if (error) {
      setError(error.message);
    } else {
      setSent(true);
    }
  };

  const handleGoogleLogin = async () => {
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-6 bg-spirit-50">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-8">
        <div className="text-center mb-8">
          <span className="text-5xl">&#9770;</span>
          <h1 className="text-3xl font-bold text-spirit-900 mt-4">Kardechat</h1>
          <p className="text-spirit-600 mt-2">
            Entre para acessar o chat
          </p>
        </div>

        {sent ? (
          <div className="text-center text-spirit-700 bg-green-50 rounded-xl p-6">
            <p className="text-lg font-medium mb-2">Link enviado!</p>
            <p>Verifique seu e-mail para acessar o Kardechat.</p>
          </div>
        ) : (
          <>
            <form onSubmit={handleLogin} className="space-y-4">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Seu e-mail"
                required
                className="w-full rounded-xl border border-spirit-300 px-4 py-3 text-spirit-800 placeholder-spirit-400 focus:outline-none focus:ring-2 focus:ring-primary-400"
              />
              <button
                type="submit"
                className="w-full bg-primary-700 hover:bg-primary-800 text-white rounded-xl px-4 py-3 font-medium transition-colors"
              >
                Entrar com e-mail
              </button>
            </form>

            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-spirit-200" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-white px-4 text-spirit-500">ou</span>
              </div>
            </div>

            <button
              onClick={handleGoogleLogin}
              className="w-full border border-spirit-300 hover:bg-spirit-50 text-spirit-700 rounded-xl px-4 py-3 font-medium transition-colors"
            >
              Entrar com Google
            </button>
          </>
        )}

        {error && (
          <p className="mt-4 text-red-600 text-sm text-center">{error}</p>
        )}
      </div>
    </div>
  );
}
