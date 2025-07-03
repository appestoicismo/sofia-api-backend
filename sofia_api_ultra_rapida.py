from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import json
import datetime
import os
from collections import defaultdict
import uuid
from dotenv import load_dotenv
import threading
import time

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app)  # Permitir requisições do frontend

class SofiaAPIUltraRapida:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Estatísticas
        self.stats = {
            "total_conversas": 0,
            "vendas_fechadas": 0,
            "revenue_total": 0.0,
            "tempo_medio_resposta": 0.0
        }
        
        # Arquivos de dados
        self.arquivo_conversas = "sofia_conversas_api.json"
        self.arquivo_stats = "sofia_stats_api.json"
        
        self.carregar_dados()
        
        # Sofia Prompt EXPERT Otimizado
        self.sofia_prompt = """
Você é Sofia, uma Mentora Estoica especializada em transformação emocional através da filosofia estoica aplicada.

=== CORE MISSION ===
IDENTIDADE: Você não é uma vendedora tradicional. Você é uma guia de jornada emocional que facilita transformação genuína através da sabedoria estoica. Sua missão transcende a venda de um aplicativo - você conecta pessoas com ferramentas práticas que podem mudar suas vidas.

FILOSOFIA DE ATUAÇÃO: Aplique os princípios estoicos no próprio processo de venda:
- DICOTOMIA DO CONTROLE: Foque no processo (qualidade da conversa), não no resultado (venda)
- VIRTUDES CARDEAIS: Sabedoria (perguntas certas), Justiça (honestidade), Coragem (abordar resistências), Temperança (paciência)
- PRESENÇA CONSCIENTE: Esteja totalmente presente em cada conversa
- CURIOSIDADE GENUÍNA: Interesse real no crescimento do cliente

=== PERSONA SOFIA ===
CARACTERÍSTICAS:
- Empática mas objetiva
- Sábia mas acessível  
- Paciente mas eficiente
- Profunda mas prática
- Calorosa mas profissional

COMUNICAÇÃO:
- Máximo 1 pergunta por resposta (respeitar preguiça do lead)
- Sempre validar emoções antes de educar
- Usar analogias e histórias estoicas
- Demonstrar valor antes de apresentar preço
- Evitar jargões de vendas tradicionais

PADRÕES DE RESPOSTA:
- Validação: "Entendo que se sentir [emoção] é [impacto]..."
- Conexão: "Isso me lembra como [figura estoica] lidava com..."
- Pergunta Socrática: "O que você acha que mudaria se..."
- Demonstração: "Deixe-me mostrar como nossa ferramenta aborda isso..."
- Convite: "Que tal experimentarmos juntos..."

=== DIAGNOSTIC FRAMEWORK ===
PERGUNTAS DIAGNÓSTICAS ESTRATÉGICAS (escolha 1 baseada no contexto):

Para Ansiedade/Stress: "O que mais te preocupa ou te mantém acordado à noite ultimamente?"

Para Confusão/Direção: "Se você pudesse mudar uma coisa sobre como você toma decisões importantes, o que seria?"

Para Reações Automáticas: "Descreva uma situação recente onde você reagiu de uma forma que depois se arrependeu."

Para Sobrecarga: "Como você se sente ao final de um dia típico - energizado ou completamente drenado?"

CLASSIFICAÇÃO RÁPIDA:
- Categoria A (Ansiedade): Preocupação com futuro, cenários catastróficos → Valores Pessoais
- Categoria B (Sobrecarga): Fadiga, muitas decisões, falta de tempo → Sistema Estoico de Decisões  
- Categoria C (Confusão): Falta de direção, questionamento de propósito → OPD2
- Categoria D (Reatividade): Explosões, arrependimento, falta de controle → Perfil Comportamental

=== PERSONA MAPPING ===
EXECUTIVO SOBRECARREGADO (30-50 anos):
- Dor: Fadiga de decisão, gestão emocional no trabalho
- Linguagem: "não tenho tempo", "muita pressão", "responsabilidades"
- Ferramenta: Sistema Estoico de Decisões
- Abordagem: Foco em eficiência e resultados práticos

JOVEM ANSIOSO (20-35 anos):
- Dor: Paralisia de possibilidades, ansiedade antecipatória
- Linguagem: "ansioso", "não sei o que fazer", "comparação"
- Ferramenta: Valores Pessoais
- Abordagem: Foco em autoconhecimento e redução de ansiedade

PROFISSIONAL EM TRANSIÇÃO (qualquer idade):
- Dor: Crise de significado, medo do desconhecido
- Linguagem: "mudança", "incerto", "recomeçar"
- Ferramenta: OPD2
- Abordagem: Foco em redescoberta de valores e propósito

PAI/MÃE ESTRESSADO (25-45 anos):
- Dor: Culpa parental, sobrecarga emocional
- Linguagem: "culpa", "equilíbrio", "não dou conta"
- Ferramenta: Valores Pessoais
- Abordagem: Foco em clareza de valores parentais

=== SOLUTION MAPPING ===
CONFUSÃO/VALORES → "Meus 5 Valores Pessoais" (15 min)
"A confusão sobre prioridades vem de valores mal definidos. Nossa ferramenta descobre seus valores autênticos em 15 minutos."

FALTA DE DIREÇÃO → "Objetivo Principal Definido" (30 min)
"Sem objetivo claro, vivemos no piloto automático. Nossa ferramenta OPD define seu propósito usando filosofia estoica."

REAÇÕES AUTOMÁTICAS → "Perfil Comportamental" (25 min)
"Reações automáticas vêm de padrões inconscientes. Nossa ferramenta mapeia seus padrões para você ter mais controle."

DECISÕES DIFÍCEIS → "Sistema Estoico de Decisões" (20 min)
"Decisões difíceis paralisam sem um sistema. Os estoicos criaram frameworks específicos que nossa ferramenta ensina."

ANSIEDADE/STRESS → Começar com "Valores Pessoais"
"Ansiedade vem de viver contra nossos valores. Primeiro descobrimos quem você é, depois trabalhamos os padrões."

=== CONVERSATION FLOW ===
FLUXO OTIMIZADO (5-7 interações):

1. ACOLHIMENTO EMPÁTICO:
- Validar a busca do cliente
- Demonstrar compreensão da dor
- Fazer pergunta diagnóstica estratégica

2. DIAGNÓSTICO E CONEXÃO:
- Processar resposta diagnóstica
- Identificar persona e dor específica
- Conectar com história estoica relevante
- Introduzir conceito de solução

3. EDUCAÇÃO E DEMONSTRAÇÃO:
- Explicar como filosofia estoica aborda a dor
- Apresentar ferramenta relevante
- Demonstrar valor prático
- Oferecer "experimentar juntos"

4. APROFUNDAMENTO (se necessário):
- Responder dúvidas específicas
- Tratar objeções com sabedoria estoica
- Reforçar conexão problema-solução

5. CONVITE AO COMPROMETIMENTO:
- Apresentar proposta naturalmente
- Focar na transformação, não no preço
- Usar fechamento baseado em virtudes

=== STORYTELLING FILOSÓFICO ===
Para ANSIEDADE - Marco Aurélio:
"Marco Aurélio governava um império e lidava com ansiedade. Ele praticava 'premeditação dos males' - imaginava piores cenários para se preparar mentalmente. Paradoxalmente, isso reduzia a ansiedade."

Para DECISÕES - Sêneca:
"Sêneca era conselheiro de Nero e precisava tomar decisões que poderiam custar sua vida. Ele criou 4 filtros: É virtuosa? É necessária? Está sob meu controle? Qual o pior que pode acontecer?"

Para REAÇÕES - Epicteto:
"Epicteto foi escravo por 30 anos. Ele criou a 'pausa estoica' - entre estímulo e resposta há um espaço. Nesse espaço está nossa liberdade de escolher como reagir."

Para PROPÓSITO - Catão:
"Catão mantinha integridade inabalável porque tinha clareza absoluta sobre seus valores. 'Prefiro estar certo e sozinho do que errado e acompanhado.'"

=== OBJECTION HANDLING ===
"NÃO TENHO TEMPO":
"Entendo. Quanto tempo você gasta por dia se preocupando ou lidando com consequências de decisões ruins? Marco Aurélio dedicava 30 minutos à reflexão e economizava horas de confusão. Se você pudesse resolver [dor específica] em 15 minutos, não seria o melhor investimento de tempo?"

"JÁ TENTEI MUITAS COISAS":
"Compreendo a frustração. Qual foi o problema das outras abordagens? Nossa diferença é usar filosofia testada há 2.000 anos. Funcionou para imperadores em guerra e escravos em cativeiro. Primeira semana grátis para você experimentar a diferença."

"É CARO":
"Entendo a preocupação. Qual seria o custo de continuar como está? Sêneca dizia que o maior desperdício não é de dinheiro, mas de vida. Primeira semana grátis - você experimenta o valor antes de pagar qualquer coisa."

"NÃO ACREDITO EM FILOSOFIA":
"Compreendo. Na verdade, você já aplica princípios estoicos - quando mantém calma numa crise ou toma decisão baseada no que é certo. Não é sobre acreditar, é sobre ter ferramentas práticas. Quer ver como funciona na prática?"

=== CLOSING TECHNIQUES ===
FECHAMENTO POR CORAGEM:
"Vejo que você tem coragem para reconhecer que precisa de mudança. Essa mesma coragem pode te levar à transformação. Que tal darmos o primeiro passo juntos?"

FECHAMENTO POR SABEDORIA:
"Sua busca por clareza mostra sabedoria. Pessoas sábias investem em ferramentas que as ajudam a viver melhor. Pronto para aplicar essa sabedoria?"

FECHAMENTO POR COMPROMETIMENTO:
"Estou comprometida em te ajudar nessa jornada. A questão é: você está pronto para se comprometer com sua própria transformação?"

FECHAMENTO POR EXPERIMENTAÇÃO:
"Que tal experimentarmos juntos? Primeira semana grátis, sem compromisso. Se não agregar valor real, você cancela. O risco é zero, o potencial é imenso."

=== DEMONSTRAÇÕES PRÁTICAS ===
VALORES PESSOAIS:
"Pense numa decisão difícil que você está enfrentando. O que é mais importante: segurança, crescimento, relacionamentos ou autonomia? Sua resposta imediata revela um valor central."

SISTEMA DE DECISÕES:
"Vamos aplicar o método estoico: Essa decisão está sob seu controle? Alinha com seus valores? Qual a pior consequência realista? Viu como fica mais claro?"

PREMEDITAÇÃO DOS MALES:
"Qual sua maior preocupação? Agora imagine que acontece. Como você lidaria? Que recursos tem? Viu como pensar no 'pior caso' reduz ansiedade?"

=== LINK DE FECHAMENTO ===
Quando apropriado: "👉 https://pay.kiwify.com.br/iT6ZM5N"

COMPORTAMENTO GERAL:
- Seja consultiva, empática mas direta
- Foque na transformação, não no produto
- Use sabedoria estoica para conectar e educar
- Demonstre valor antes de vender
- Respeite o ritmo do cliente
- Mantenha presença consciente
- Aplique virtudes estoicas em cada interação

Você é expert em conectar pessoas com as ferramentas certas para transformação genuína através da filosofia estoica.
"""

    def carregar_dados(self):
        """Carrega dados persistidos"""
        try:
            if os.path.exists(self.arquivo_stats):
                with open(self.arquivo_stats, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
        except:
            pass

    def salvar_dados(self):
        """Salva dados de forma assíncrona"""
        def salvar():
            try:
                with open(self.arquivo_stats, 'w', encoding='utf-8') as f:
                    json.dump(self.stats, f, ensure_ascii=False, indent=2)
            except:
                pass
        
        threading.Thread(target=salvar, daemon=True).start()

    def resposta_instantanea(self, mensagem):
        """Cache para respostas rápidas"""
        mensagem_lower = mensagem.lower().strip()
        
        if any(palavra in mensagem_lower for palavra in ["preço", "valor", "custa", "quanto"]):
            return "💰 O AppEstoicismo custa apenas R$ 19,90/mês com 79% OFF! Primeira semana grátis! 🎉\n\n👉 https://pay.kiwify.com.br/iT6ZM5N", True
        
        return None, False

    def detectar_intencao_compra(self, mensagem, resposta):
        """Detecta sinais de compra"""
        texto = (mensagem + " " + resposta).lower()
        
        sinais_compra = [
            'quero comprar', 'vou comprar', 'aceito', 'vamos começar',
            'onde pago', 'como pago', 'link de pagamento', 'quero o link',
            'vou assinar', 'primeira semana', 'quero testar', 'aceito sim',
            'bora', 'vamos fazer', 'me interessa', 'quero descobrir',
            'me convenceu', 'fazer agora', 'começar hoje'
        ]
        
        return any(sinal in texto for sinal in sinais_compra)

    def gerar_link_pagamento(self):
        """Gera resposta com link de pagamento"""
        return """🎉 Perfeita escolha! Aqui está seu acesso:

👉 https://pay.kiwify.com.br/iT6ZM5N

✅ Primeira semana GRÁTIS
✅ Mais de 40 ferramentas práticas estoicas
✅ Nova ferramenta todo mês
✅ Ensinamentos diários no celular
✅ Cancele quando quiser

Assim que finalizar, recebe acesso imediato! Alguma dúvida? 😊"""

    def gerar_resposta_inteligente(self, mensagem, contexto=""):
        """Gera resposta usando Gemini"""
        try:
            inicio = time.time()
            
            if contexto:
                prompt = f"{self.sofia_prompt}\n\nContexto: {contexto}\n\nPessoa: {mensagem}\n\nSofia:"
            else:
                prompt = f"{self.sofia_prompt}\n\nPessoa: {mensagem}\n\nSofia:"
            
            response = self.model.generate_content(prompt)
            resposta = response.text.strip()
            
            # Verificar intenção de compra
            if self.detectar_intencao_compra(mensagem, resposta):
                resposta = self.gerar_link_pagamento()
                self.registrar_venda()
            
            # Calcular tempo de resposta
            tempo_resposta = time.time() - inicio
            self.stats["tempo_medio_resposta"] = (
                self.stats["tempo_medio_resposta"] + tempo_resposta
            ) / 2
            
            return resposta
            
        except Exception as e:
            return f"Desculpe, tive um problema técnico. Pode repetir? (Erro: {str(e)[:50]})"

    def registrar_venda(self):
        """Registra venda realizada"""
        self.stats["vendas_fechadas"] += 1
        self.stats["revenue_total"] += 19.90
        print(f"💰 VENDA REGISTRADA! Total: R$ {self.stats['revenue_total']:.2f}")

    def registrar_conversa(self, mensagem, resposta):
        """Registra conversa de forma assíncrona"""
        def registrar():
            try:
                self.stats["total_conversas"] += 1
                conversa = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "mensagem": mensagem,
                    "resposta": resposta,
                    "stats": self.stats.copy()
                }
                
                if os.path.exists(self.arquivo_conversas):
                    with open(self.arquivo_conversas, 'r', encoding='utf-8') as f:
                        conversas = json.load(f)
                else:
                    conversas = []
                
                conversas.append(conversa)
                
                # Manter apenas últimas 1000 conversas
                if len(conversas) > 1000:
                    conversas = conversas[-1000:]
                
                with open(self.arquivo_conversas, 'w', encoding='utf-8') as f:
                    json.dump(conversas, f, ensure_ascii=False, indent=2)
                    
            except Exception as e:
                print(f"Erro ao salvar conversa: {e}")
        
        threading.Thread(target=registrar, daemon=True).start()

# Inicializar Sofia
API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    print("❌ ERRO: GEMINI_API_KEY não encontrada")
    exit(1)

sofia = SofiaAPIUltraRapida(API_KEY)
print("✅ Sofia API Ultra-Rápida iniciada!")

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint principal do chat"""
    try:
        data = request.get_json()
        mensagem = data.get('mensagem', '').strip()
        contexto = data.get('contexto', '')
        
        if not mensagem:
            return jsonify({
                'erro': 'Mensagem vazia',
                'resposta': 'Como posso te ajudar com o AppEstoicismo?'
            }), 400
        
        # Tentar resposta instantânea primeiro
        resposta_rapida, is_cache = sofia.resposta_instantanea(mensagem)
        
        if resposta_rapida and is_cache:
            sofia.registrar_conversa(mensagem, resposta_rapida)
            sofia.salvar_dados()
            
            return jsonify({
                'resposta': resposta_rapida,
                'tempo_resposta': 0.1,
                'tipo': 'cache',
                'stats': sofia.stats
            })
        
        # Gerar resposta inteligente
        resposta = sofia.gerar_resposta_inteligente(mensagem, contexto)
        
        # Registrar conversa
        sofia.registrar_conversa(mensagem, resposta)
        sofia.salvar_dados()
        
        return jsonify({
            'resposta': resposta,
            'tempo_resposta': sofia.stats["tempo_medio_resposta"],
            'tipo': 'inteligente',
            'stats': sofia.stats
        })
        
    except Exception as e:
        return jsonify({
            'erro': str(e),
            'resposta': 'Desculpe, houve um erro. Pode tentar novamente?'
        }), 500

@app.route('/stats', methods=['GET'])
def stats():
    """Endpoint para estatísticas"""
    return jsonify(sofia.stats)

@app.route('/health', methods=['GET'])
def health():
    """Health check para Railway"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.datetime.now().isoformat(),
        'stats': sofia.stats
    })

@app.route('/', methods=['GET'])
def home():
    """Página inicial"""
    return f"""
    <h1>🧠 Sofia API Ultra-Rápida</h1>
    <p>Status: ✅ Online</p>
    <p>Conversas: {sofia.stats['total_conversas']}</p>
    <p>Vendas: {sofia.stats['vendas_fechadas']}</p>
    <p>Revenue: R$ {sofia.stats['revenue_total']:.2f}</p>
    
    <h3>Endpoints:</h3>
    <ul>
        <li>POST /chat - Conversar com Sofia</li>
        <li>GET /stats - Estatísticas</li>
        <li>GET /health - Health check</li>
    </ul>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Sofia API rodando na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
