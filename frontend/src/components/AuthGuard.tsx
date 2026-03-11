"use client";

// Auth desabilitado temporariamente – integração Supabase pendente.
// TODO: reativar quando o produto estiver pronto.

interface AuthGuardProps {
  children: () => React.ReactNode;
}

export default function AuthGuard({ children }: AuthGuardProps) {
  return <>{children()}</>;
}
