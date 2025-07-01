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
        
        # Cache para respostas rápidas
        self.cache_respostas = {
            "oi": "Olá! Sou a Sofia, sua consultora estoica. Como posso te ajudar hoje? 😊",
            "olá": "Oi! Que bom te ver aqui! Sou a Sofia. Em que posso te ajudar?",
            "help": "Estou aqui para te ajudar com desenvolvimento mental através da filosofia estoica!",
            "preço": "O AppEstoicismo custa apenas R$ 19,90/mês com 79% OFF! Primeira semana grátis! 🎉"
        }
        
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
        
        # Sofia Prompt Otimizado
        self.sofia_prompt = """
Você é Sofia, consultora estoica inteligente do AppEstoicismo. Seja natural, empática e focada em vendas consultivas.

PRODUTO: AppEstoicismo - R$ 19,90/mês (79% OFF), primeira semana grátis
LINK: https://pay.kiwify.com.br/iT6ZM5N

PERSONALIDADE:
- Natural e consultiva (não robótica)
- Empática mas focada em resultados
- Faz perguntas para entender necessidades
- Conduz para venda de forma sutil

SINAIS DE COMPRA (gere link automaticamente):
- "quero comprar", "vou assinar", "aceito"
- "onde pago", "como pago", "me manda o link"
- "vamos começar", "quero começar"

ESTRATÉGIA:
1. Rapport rápido
2. Identificar dor/necessidade
3. Apresentar solução
4. Conduzir ao fechamento

Seja concisa (máximo 3 linhas) mas eficaz.
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
        """Resposta cache para velocidade"""
        mensagem_lower = mensagem.lower().strip()
        
        # Respostas em cache
        for key in self.cache_respostas:
            if key in mensagem_lower:
                return self.cache_respostas[key], True
        
        # Resposta genérica rápida
        if len(mensagem_lower) < 10:
            return "Oi! Me conte mais sobre isso...", False
        
        return None, False

    def detectar_intencao_compra(self, mensagem, resposta):
        """Detecta sinais de compra"""
        texto = (mensagem + " " + resposta).lower()
        
        sinais_compra = [
            'quero comprar', 'vou comprar', 'aceito', 'vamos começar',
            'onde pago', 'como pago', 'link de pagamento', 'quero o link',
            'me manda o link', 'vou assinar', 'primeira semana'
        ]
        
        return any(sinal in texto for sinal in sinais_compra)

    def gerar_link_pagamento(self):
        """Gera resposta com link de pagamento"""
        return """🎉 Perfeita escolha! Aqui está seu acesso:

👉 https://pay.kiwify.com.br/iT6ZM5N

✅ Primeira semana GRÁTIS
✅ Depois R$ 19,90/mês (79% OFF)
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
    print("❌ ERRO: GEMINI_API_KEY não encontrada no .env")
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
                'resposta': 'Olá! Como posso ajudar?'
            }), 400
        
        # Tentar resposta instantânea primeiro
        resposta_rapida, is_cache = sofia.resposta_instantanea(mensagem)
        
        if resposta_rapida and is_cache:
            # Resposta em cache - instantânea
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
    <p>Tempo médio: {sofia.stats['tempo_medio_resposta']:.2f}s</p>
    
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
    print(f"💰 Revenue atual: R$ {sofia.stats['revenue_total']:.2f}")
    app.run(host='0.0.0.0', port=port, debug=False)
