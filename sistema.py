#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Citizen Assist AI
Assistente introdutório de orientação cidadã baseado em uma base JSON local.

Execução na raiz do repositório:
    python src/sistema.py

O programa não é um canal oficial e não substitui orientação profissional.
"""

import json
import re
import sys
import time
import unicodedata
from pathlib import Path
from collections import defaultdict


def caminho_base():
    """Localiza data/base.json a partir da raiz do projeto."""
    raiz = Path(__file__).resolve().parent.parent
    return raiz / "data" / "base.json"


def normalizar(texto):
    """Remove acentos, converte para minúsculas e normaliza espaços."""
    texto = unicodedata.normalize("NFD", str(texto).lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]+", " ", texto).strip()


def carregar_base(caminho=None):
    """Carrega e valida a estrutura mínima da base JSON."""
    arquivo = Path(caminho) if caminho else caminho_base()
    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo de base não encontrado: {arquivo}")
    if arquivo.stat().st_size == 0:
        raise ValueError("O arquivo base.json está vazio.")

    with arquivo.open("r", encoding="utf-8") as f:
        dados = json.load(f)

    if not isinstance(dados, dict) or not isinstance(dados.get("orientacoes"), list):
        raise ValueError("Estrutura inválida: esperado um objeto com a lista 'orientacoes'.")

    obrigatorios = {"id", "tema", "subtema", "pergunta", "palavras_chave",
                    "orientacao", "referencia", "url", "data_verificacao"}
    ids = set()
    for numero, item in enumerate(dados["orientacoes"], start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Registro {numero} não é um objeto JSON.")
        faltantes = obrigatorios - set(item)
        if faltantes:
            raise ValueError(f"Registro {numero} sem campos: {', '.join(sorted(faltantes))}")
        if not all(item[campo] for campo in obrigatorios - {"palavras_chave"}):
            raise ValueError(f"Registro {numero} possui campo obrigatório vazio.")
        if not isinstance(item["palavras_chave"], list):
            raise ValueError(f"Palavras-chave inválidas no registro {item['id']}.")
        if item["id"] in ids:
            raise ValueError(f"Identificador duplicado: {item['id']}")
        ids.add(item["id"])

    return dados


def pontuar(pergunta, registro):
    """Calcula correspondência lexical usando apenas campos de identificação."""
    consulta = normalizar(pergunta)
    if not consulta:
        return 0.0

    stopwords = {
        "a", "as", "o", "os", "um", "uma", "uns", "umas", "de", "da", "do",
        "das", "dos", "em", "no", "na", "nos", "nas", "por", "para", "com",
        "e", "ou", "que", "como", "qual", "quais", "meu", "minha", "meus",
        "minhas", "eu", "voce", "vocês", "preciso", "quero", "fazer", "onde",
        "está", "esta", "isso", "esse", "essa", "muito", "mais", "sobre"
    }
    termos = {t for t in consulta.split() if t not in stopwords and len(t) > 2}
    if not termos:
        return 0.0

    campos = [
        registro.get("tema", ""),
        registro.get("subtema", ""),
        registro.get("pergunta", ""),
        " ".join(registro.get("palavras_chave", []))
    ]
    texto = normalizar(" ".join(campos))
    palavras_registro = set(texto.split())
    cobertura = len(termos & palavras_registro) / len(termos)

    bonus = 0.0
    for chave in registro.get("palavras_chave", []):
        chave_norm = normalizar(chave)
        if len(chave_norm) > 3 and chave_norm in consulta:
            bonus = max(bonus, 0.30)

    pergunta_base = normalizar(registro.get("pergunta", ""))
    if pergunta_base and (pergunta_base in consulta or consulta in pergunta_base):
        bonus = max(bonus, 0.35)

    return min(cobertura + bonus, 1.0)


def buscar(pergunta, dados, limite=0.30):
    """
    Retorna o registro de maior pontuação e a pontuação.
    O limite evita responder quando há pouca evidência lexical.
    """
    if not isinstance(pergunta, str) or not pergunta.strip():
        return None, 0.0

    resultados = [(pontuar(pergunta, item), item) for item in dados["orientacoes"]]
    resultados.sort(key=lambda par: par[0], reverse=True)
    if not resultados or resultados[0][0] < limite:
        return None, resultados[0][0] if resultados else 0.0

    melhor_pontuacao, melhor = resultados[0]
    # Se os dois melhores resultados forem muito próximos, não assumir certeza.
    if len(resultados) > 1 and melhor_pontuacao - resultados[1][0] < 0.04:
        return None, melhor_pontuacao
    return melhor, melhor_pontuacao


def exibir_orientacao(registro, pontuacao=None):
    """Apresenta a orientação e sua referência."""
    print("\n" + "=" * 68)
    print(f"[{registro['id']}] {registro['tema']} > {registro['subtema']}")
    print("\nOrientação:")
    print(registro["orientacao"])
    print("\nPróximo passo:")
    print("Leia a fonte oficial e confirme os requisitos, prazos e canais aplicáveis.")
    print(f"\nFonte: {registro['referencia']}")
    print(f"Link: {registro['url']}")
    print(f"Data de verificação registrada: {registro['data_verificacao']}")
    if registro.get("confirmacao_adicional", True):
        print("Aviso: confirme a informação no órgão responsável; regras podem mudar.")
    if pontuacao is not None:
        print(f"Indicador interno de correspondência lexical: {pontuacao:.2f}")
    print("=" * 68)


def exibir_temas(dados):
    temas = sorted({item["tema"] for item in dados["orientacoes"]})
    print("\nTemas disponíveis:")
    for indice, tema in enumerate(temas, start=1):
        total = sum(1 for item in dados["orientacoes"] if item["tema"] == tema)
        print(f"{indice}. {tema} ({total} orientações)")


def consultar_tema(tema, dados):
    encontrados = [r for r in dados["orientacoes"]
                   if normalizar(r["tema"]) == normalizar(tema)]
    if not encontrados:
        print("Tema não encontrado. Escolha um dos temas exibidos no menu.")
        return
    print(f"\nOrientações de {tema}:")
    for i, item in enumerate(encontrados, start=1):
        print(f"{i}. {item['subtema']} — {item['pergunta']}")
    escolha = input("Digite o número da orientação ou Enter para voltar: ").strip()
    if not escolha:
        return
    if not escolha.isdigit() or not 1 <= int(escolha) <= len(encontrados):
        print("Opção inválida. Digite um número da lista.")
        return
    exibir_orientacao(encontrados[int(escolha) - 1])


def mostrar_relacionados(tema, dados):
    """Navegação temática simples, representada como grafo por lista de adjacência."""
    grafo = dados.get("navegacao", {})
    relacionados = grafo.get(tema, [])
    if relacionados:
        print("\nAssuntos relacionados para continuar:")
        for assunto in relacionados:
            print(f"- {assunto}")


def responder(pergunta, dados, mostrar=True):
    inicio = time.perf_counter()
    registro, score = buscar(pergunta, dados)
    duracao = time.perf_counter() - inicio
    if registro and mostrar:
        exibir_orientacao(registro, score)
        mostrar_relacionados(registro["tema"], dados)
    elif mostrar:
        if not pergunta.strip():
            print("A consulta está vazia. Digite uma pergunta ou escolha um tema.")
        else:
            print("Não encontrei uma orientação suficientemente relacionada na base.")
            print("Não vou inventar uma resposta. Tente reformular ou escolha um tema:")
            exibir_temas(dados)
    return (registro["id"] if registro else None), duracao, score


def executar_testes(dados, mostrar=True):
    """Executa perguntas de teste da base e calcula taxa de acerto e tempo médio."""
    testes = dados.get("perguntas_teste", [])
    if not testes:
        print("Não há perguntas de teste cadastradas.")
        return

    acertos = 0
    tempos = []
    linhas = []
    for teste in testes:
        obtido, duracao, _ = responder(teste["pergunta"], dados, mostrar=False)
        esperado = teste.get("esperado")
        correto = obtido == esperado
        acertos += int(correto)
        tempos.append(duracao)
        linhas.append((teste["pergunta"], esperado, obtido, correto, duracao))

    taxa = (acertos / len(testes)) * 100
    media = sum(tempos) / len(tempos) if tempos else 0
    if mostrar:
        print("\nRESULTADO DOS TESTES")
        print("-" * 90)
        for pergunta, esperado, obtido, correto, duracao in linhas:
            status = "ACERTO" if correto else "ERRO"
            print(f"{status:6} | Esperado: {str(esperado):6} | Obtido: {str(obtido):6} | "
                  f"{duracao * 1000:.3f} ms | {pergunta or '[entrada vazia]'}")
        print("-" * 90)
        print(f"Perguntas executadas: {len(testes)}")
        print(f"Acertos: {acertos}")
        print(f"Taxa de acerto: {taxa:.1f}%")
        print(f"Tempo médio de busca: {media * 1000:.3f} ms")
        print("\nLimitações: conjunto pequeno e elaborado manualmente; a taxa mede apenas")
        print("a correspondência com os resultados esperados cadastrados, não a verdade")
        print("completa da orientação nem a satisfação de todos os usuários.")
    return {"total": len(testes), "acertos": acertos, "taxa_acerto": taxa,
            "tempo_medio_segundos": media, "resultados": linhas}


def comparar_prompts(dados):
    print("\nMODELOS DE INSTRUÇÃO / PROMPT")
    print("\nModelo 1 — Direto:")
    print(dados.get("prompts", {}).get("modelo_1_direto", "Não cadastrado."))
    print("\nModelo 2 — Estruturado:")
    print(dados.get("prompts", {}).get("modelo_2_estruturado", "Não cadastrado."))
    print("\nComparação: o modelo 1 é mais curto e simples. O modelo 2 define campos")
    print("obrigatórios e explicita melhor os limites, facilitando a avaliação da saída.")
    print("Este protótipo aplica essas instruções como regras de formatação; não chama")
    print("um modelo externo de IA.")


def menu(dados):
    while True:
        print("\n" + "=" * 68)
        print("CITIZEN ASSIST AI — Assistente introdutório de orientação cidadã")
        print("=" * 68)
        print("1. Fazer uma pergunta")
        print("2. Consultar por tema")
        print("3. Ver temas disponíveis")
        print("4. Executar testes e métricas")
        print("5. Comparar modelos de prompt")
        print("6. Sobre, privacidade e limitações")
        print("0. Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            pergunta = input("\nDigite sua pergunta: ")
            responder(pergunta, dados)
        elif opcao == "2":
            exibir_temas(dados)
            tema = input("\nDigite o nome do tema: ").strip()
            consultar_tema(tema, dados)
        elif opcao == "3":
            exibir_temas(dados)
            tema = input("\nDigite um tema para ver assuntos relacionados (ou Enter): ").strip()
            if tema:
                mostrar_relacionados(tema, dados)
        elif opcao == "4":
            executar_testes(dados)
        elif opcao == "5":
            comparar_prompts(dados)
        elif opcao == "6":
            print("\nEste protótipo organiza orientações introdutórias com referências.")
            print("Não é canal oficial, não garante elegibilidade a benefícios e não")
            print("substitui atendimento de órgãos públicos ou aconselhamento profissional.")
            print("Não informe CPF, senhas, endereço, dados bancários ou outros dados pessoais.")
            print("As fontes e datas devem ser revisadas periodicamente pela equipe.")
        elif opcao == "0":
            print("Obrigado por utilizar o Citizen Assist AI.")
            break
        else:
            print("Opção inválida. Escolha uma opção exibida no menu.")


def main():
    try:
        dados = carregar_base()
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as erro:
        print(f"Não foi possível iniciar o assistente: {erro}")
        print("Verifique se data/base.json existe e está preenchido corretamente.")
        sys.exit(1)

    print(f"Base carregada: {len(dados['orientacoes'])} orientações.")
    menu(dados)


if __name__ == "__main__":
    main()
