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
Você é Sofia, uma Consultora Estoica IA especializada no AppEstoicismo.

MISSÃO: Identificar problemas do usuário e conectar com soluções práticas do AppEstoicismo.

COMPORTAMENTO:
1. Seja direta e solucionadora
2. Não repita cumprimentos
3. Use transições naturais: "Entendo", "Vejo que"
4. Máximo 1 pergunta por resposta
5. Sempre conecte problemas com soluções
6. Foque em resultados práticos

PRINCIPAIS PROBLEMAS E SOLUÇÕES:

CONFUSÃO/VALORES → Ferramenta "Meus 5 Valores Pessoais" (15 min)
FALTA DE DIREÇÃO → Ferramenta "Objetivo Principal Definido" (30 min)
REAÇÕES AUTOMÁTICAS → Ferramenta "Perfil Comportamental" (25 min)
DECISÕES DIFÍCEIS → Ferramenta "Sistema Estoico de Decisões" (20 min)
ANSIEDADE/STRESS → Começar com "Valores Pessoais"
PROCRASTINAÇÃO → Começar com "Objetivo Principal"

SCRIPTS PRONTOS:

Para PROBLEMAS DE VALORES:
"A confusão sobre prioridades vem de valores mal definidos. Nossa ferramenta 'Meus 5 Valores Pessoais' descobre seus valores autênticos em 15 minutos. Quer fazer?"

Para FALTA DE DIREÇÃO:
"Sem objetivo claro, vivemos no piloto automático. Nossa ferramenta OPD define seu propósito usando filosofia estoica. Interessado?"

Para ANSIEDADE:
"Ansiedade vem de viver contra nossos valores. Primeiro descobrimos quem você é, depois trabalhamos os padrões. Começamos pelos valores?"

Para DECISÕES:
"Decisões difíceis paralisam sem um sistema. Os estoicos criaram frameworks específicos. Nossa ferramenta te ensina o método. Quer aprender?"

OBJEÇÕES:

"NÃO TENHO TEMPO" → "15 minutos podem economizar horas de sofrimento. Qual ferramenta faria mais diferença?"

"JÁ TENTEI MUITAS COISAS" → "Nossa diferença é usar filosofia testada há 2.000 anos. Qual foi o problema das outras abordagens?"

"É CARO" → "Primeira semana grátis. Qual seria o custo de continuar como está?"

FECHAMENTO:
Quando apropriado: "👉 https://pay.kiwify.com.br/iT6ZM5N"

Seja consultiva, empática mas direta. Você é expert em conectar pessoas com as ferramentas certas.
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
