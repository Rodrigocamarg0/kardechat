"use client";

import { useRouter } from "next/navigation";

export default function LandingPage() {
  const router = useRouter();

  return (
    <main className="min-h-screen flex flex-col">
      {/* Hero */}
      <section className="flex-1 flex items-center justify-center px-6 py-20">
        <div className="max-w-3xl text-center">
          <div className="mb-8">
            <span className="text-6xl">&#9770;</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-spirit-900 mb-6 leading-tight">
            Kardechat
          </h1>
          <p className="text-xl md:text-2xl text-spirit-700 mb-4 text-balance">
            A sabedoria de Allan Kardec ao alcance de uma conversa.
          </p>
          <p className="text-lg text-spirit-600 mb-10 max-w-2xl mx-auto">
            Faça perguntas e receba respostas baseadas nos 5 livros do
            Pentateuco Espírita. Nosso sistema encontra as passagens mais
            relevantes diretamente nas obras originais.
          </p>
          <button
            onClick={() => router.push("/chat")}
            className="bg-primary-700 hover:bg-primary-800 text-white text-lg px-10 py-4 rounded-xl shadow-lg transition-all hover:shadow-xl hover:scale-105 active:scale-100"
          >
            Iniciar Conversa
          </button>
        </div>
      </section>

      {/* Features */}
      <section className="bg-white/60 backdrop-blur px-6 py-16">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-spirit-900 text-center mb-12">
            Como funciona
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon="&#128218;"
              title="Busca Inteligente"
              description="Encontramos a pergunta mais parecida com a sua no Livro dos Espíritos, usando correspondência semântica avançada."
            />
            <FeatureCard
              icon="&#128214;"
              title="5 Livros Completos"
              description="Quando a resposta não está no L.E., buscamos nos demais livros do Pentateuco: Médiuns, Evangelho, Céu e Inferno e Gênese."
            />
            <FeatureCard
              icon="&#128221;"
              title="Citações Originais"
              description="Cada resposta inclui as citações dos trechos originais dos livros de Kardec. Transparência total."
            />
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="px-6 py-16">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-spirit-900 text-center mb-12">
            Sistema de Confiança
          </h2>
          <div className="space-y-6">
            <ConfidenceLevel
              level="Alta"
              color="bg-green-100 border-green-400"
              description="Quando encontramos uma pergunta muito similar no Livro dos Espíritos, retornamos a resposta original diretamente."
            />
            <ConfidenceLevel
              level="Média"
              color="bg-yellow-100 border-yellow-400"
              description="Quando a similaridade é moderada, sintetizamos a resposta a partir das perguntas mais relacionadas."
            />
            <ConfidenceLevel
              level="Exploratória"
              color="bg-blue-100 border-blue-400"
              description="Para temas mais amplos, buscamos nos 5 livros completos e elaboramos uma resposta fundamentada."
            />
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-spirit-900 text-white px-6 py-16 text-center">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold mb-4">
            Pronto para explorar a Doutrina Espírita?
          </h2>
          <p className="text-spirit-200 mb-8 text-lg">
            Gratuito e open source. Baseado nas obras originais de Allan Kardec.
          </p>
          <button
            onClick={() => router.push("/chat")}
            className="bg-white text-spirit-900 text-lg px-10 py-4 rounded-xl shadow-lg hover:bg-spirit-50 transition-all hover:scale-105 active:scale-100"
          >
            Começar Agora
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-spirit-900 border-t border-spirit-800 text-spirit-400 text-center py-6 text-sm">
        <p>
          Kardechat &mdash; Projeto open source. As obras de Allan Kardec são de
          domínio público.
        </p>
      </footer>
    </main>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-bold text-spirit-900 mb-2">{title}</h3>
      <p className="text-spirit-600">{description}</p>
    </div>
  );
}

function ConfidenceLevel({
  level,
  color,
  description,
}: {
  level: string;
  color: string;
  description: string;
}) {
  return (
    <div className={`border-l-4 ${color} rounded-r-lg p-5`}>
      <h3 className="font-bold text-spirit-900 mb-1">
        Confiança {level}
      </h3>
      <p className="text-spirit-700">{description}</p>
    </div>
  );
}
