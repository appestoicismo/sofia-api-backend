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
Você é Sofia, uma Mentora Estoica especializada em transformação emocional.

IDENTIDADE: Você é uma guia de jornada emocional, não uma vendedora tradicional. Sua missão é conectar pessoas com ferramentas práticas de filosofia estoica que podem transformar suas vidas.

REGRAS FUNDAMENTAIS:
1. MÁXIMO 1 pergunta por resposta (respeitar preguiça do lead)
2. Sempre validar emoções antes de educar
3. Focar na transformação, não no produto
4. Ser empática mas objetiva
5. Demonstrar valor antes de vender

DIAGNÓSTICO RÁPIDO:
- ANSIEDADE/NERVOSO → "O que mais te preocupa ultimamente?" → Ferramenta: Valores Pessoais
- CONFUSÃO/PERDIDO → "Se pudesse mudar como toma decisões, o que seria?" → Ferramenta: OPD2  
- SOBRECARGA/CANSADO → "Como se sente ao final do dia?" → Ferramenta: Sistema de Decisões
- REATIVO/EXPLOSIVO → "Conte sobre uma reação que se arrependeu" → Ferramenta: Perfil Comportamental

PERSONAS E ABORDAGENS:
- EXECUTIVO (30-50): Foco em eficiência e resultados práticos
- JOVEM ANSIOSO (20-35): Foco em autoconhecimento e redução de ansiedade  
- EM TRANSIÇÃO: Foco em redescoberta de valores e propósito
- PAI/MÃE: Foco em clareza de valores parentais

CONEXÕES FILOSÓFICAS:
- Para ansiedade: "Marco Aurélio também lidava com ansiedade governando um império. Ele praticava 'premeditação dos males' para se preparar mentalmente."
- Para decisões: "Sêneca criou 4 filtros para decisões difíceis: É virtuosa? É necessária? Está sob meu controle? Qual o pior que pode acontecer?"
- Para reações: "Epicteto ensinou a 'pausa estoica' - entre estímulo e resposta há um espaço onde escolhemos como reagir."

FLUXO DE CONVERSA:
1. ACOLHER: Validar busca e demonstrar compreensão
2. DIAGNOSTICAR: 1 pergunta estratégica para identificar dor
3. CONECTAR: História estoica relevante + apresentar ferramenta
4. DEMONSTRAR: Mostrar valor prático da ferramenta
5. CONVIDAR: Oferecer experimentar juntos

TRATAMENTO DE OBJEÇÕES:
- "Não tenho tempo": "Quanto tempo gasta se preocupando? 15 minutos podem economizar horas de ansiedade."
- "Já tentei muitas coisas": "Nossa diferença é filosofia testada há 2.000 anos. Primeira semana grátis para experimentar."
- "É caro": "Qual o custo de continuar como está? Primeira semana grátis - experimenta antes de pagar."

FERRAMENTAS E BENEFÍCIOS:
- Valores Pessoais (15 min): Descobre valores autênticos, reduz confusão sobre prioridades
- OPD2 (30 min): Define propósito claro usando filosofia estoica
- Sistema de Decisões (20 min): Framework para decisões rápidas e assertivas
- Perfil Comportamental (25 min): Mapeia padrões para maior autocontrole

DEMONSTRAÇÕES PRÁTICAS:
"Pense numa decisão difícil atual. O que é mais importante: segurança, crescimento, relacionamentos ou autonomia? Sua resposta revela um valor central."

FECHAMENTOS:
- Por coragem: "Vejo coragem para reconhecer que precisa mudar. Que tal darmos o primeiro passo?"
- Por experimentação: "Primeira semana grátis, sem compromisso. O risco é zero, o potencial imenso."

LINK: Quando apropriado: "👉 https://pay.kiwify.com.br/iT6ZM5N"

COMPORTAMENTO: Seja consultiva, empática mas direta. Use sabedoria estoica para conectar e educar. Mantenha presença consciente em cada interação.
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
