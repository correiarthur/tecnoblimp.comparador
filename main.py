import pandas as pd
import json
import logging
import os
import sys

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("processamento.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def carregar_configuracao(caminho_config='settings.json'):
    """Carrega o arquivo de configuração JSON."""
    try:
        # Se o arquivo não existir, retorna um dict vazio ou padrão para evitar crash
        if not os.path.exists(caminho_config):
            logging.warning(f"Arquivo de configuração '{caminho_config}' não encontrado. Usando padrões.")
            return {}
        
        with open(caminho_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logging.info("Configuração carregada com sucesso.")
        return config
    except Exception as e:
        logging.error(f"Erro ao carregar configuração: {e}")
        return {}

def carregar_dados(caminho_arquivo):
    """Carrega um arquivo Excel para um DataFrame Pandas a partir de um caminho."""
    try:
        if not os.path.exists(caminho_arquivo):
            raise FileNotFoundError(f"Arquivo de dados '{caminho_arquivo}' não encontrado.")
        
        df = pd.read_excel(caminho_arquivo)
        df = df.astype(str)
        logging.info(f"Arquivo '{caminho_arquivo}' carregado: {df.shape[0]} registros.")
        return df
    except Exception as e:
        logging.error(f"Erro ao ler arquivo '{caminho_arquivo}': {e}")
        return None

def validar_colunas(df, colunas_necessarias, nome_arquivo):
    """Verifica se as colunas necessárias existem no DataFrame."""
    colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
    if colunas_faltantes:
        logging.error(f"Colunas faltantes no arquivo '{nome_arquivo}': {colunas_faltantes}")
        return False
    return True

def criar_chave(df, colunas):
    """Cria uma série com a chave concatenada das colunas informadas."""
    return df[colunas].astype(str).agg(''.join, axis=1)

def processar_comparacao(df_carga, df_sistema, config):
    """
    Executa a lógica de comparação entre dois DataFrames já carregados.
    Retorna: (df_analise, inconsistencias_encontradas)
    """
    df_analise = df_carga.copy()
    inconsistencias_encontradas = []
    
    # 1. Validações Dinâmicas
    validacoes = config.get('validacoes', [])
    
    for validacao in validacoes:
        nome_validacao = validacao.get('nome_verificacao')
        cols = validacao.get('colunas_chave')
        
        if not validar_colunas(df_carga, cols, "Carga") or not validar_colunas(df_sistema, cols, "Sistema"):
            logging.warning(f"Pulando validação '{nome_validacao}' por falta de colunas.")
            continue
            
        chave_carga = criar_chave(df_analise, cols)
        chave_sistema = criar_chave(df_sistema, cols)
        
        set_chaves_sistema = set(chave_sistema)
        
        df_analise[nome_validacao] = chave_carga.apply(
            lambda x: 'Localizado' if x in set_chaves_sistema else 'Não Localizado'
        )

        qtd_nao_loc = (df_analise[nome_validacao] == 'Não Localizado').sum()
        msg = f"Validação '{nome_validacao}': {qtd_nao_loc} registros não localizados."
        logging.info(msg)
        
        if qtd_nao_loc > 0:
            inconsistencias_encontradas.append(msg)

    # 2. Validação Final
    val_final = config.get('validacao_final', {})
    cols_final = val_final.get('colunas_chave', [])
    nome_col_final = val_final.get('nome_coluna', 'Resultado')

    if cols_final: # Só executa se houver configuração
        if validar_colunas(df_analise, cols_final, "Carga") and validar_colunas(df_sistema, cols_final, "Sistema"):
            chave_final_carga = criar_chave(df_analise, cols_final)
            chave_final_sistema = criar_chave(df_sistema, cols_final)
            set_final_sistema = set(chave_final_sistema)

            df_analise[nome_col_final] = chave_final_carga.apply(
                lambda x: 'Localizado' if x in set_final_sistema else 'Não Localizado'
            )
            
            qtd_final_nao_loc = (df_analise[nome_col_final] == 'Não Localizado').sum()
            msg_final = f"Resultado Final ('{nome_col_final}'): {qtd_final_nao_loc} registros com divergência total."
            logging.info(msg_final)
            if qtd_final_nao_loc > 0:
                inconsistencias_encontradas.append(msg_final)
                
    return df_analise, inconsistencias_encontradas

def main():
    config = carregar_configuracao()
    
    arquivos_config = config.get('arquivos', {})
    caminho_carga = arquivos_config.get('carga')
    caminho_sistema = arquivos_config.get('sistema')
    caminho_saida = arquivos_config.get('saida_analise')
    caminho_relatorio = arquivos_config.get('relatorio_erros')

    logging.info("Iniciando carregamento dos dados via arquivo...")
    df_carga = carregar_dados(caminho_carga)
    df_sistema = carregar_dados(caminho_sistema)

    if df_carga is None or df_sistema is None:
        logging.critical("Falha no carregamento dos arquivos. Abortando execução.")
        sys.exit(1)

    logging.info("Iniciando processamento...")
    df_analise, inconsistencias = processar_comparacao(df_carga, df_sistema, config)
    
    # Exportação
    try:
        logging.info(f"Exportando resultados para '{caminho_saida}'...")
        with pd.ExcelWriter(caminho_saida) as writer:
            df_carga.to_excel(writer, sheet_name='DadosCarga', index=False)
            df_sistema.to_excel(writer, sheet_name='DadosSistema', index=False)
            df_analise.to_excel(writer, sheet_name='Analise', index=False)
        logging.info("Arquivo de análise exportado com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao exportar Excel: {e}")

    # Relatório Texto
    try:
        with open(caminho_relatorio, 'w', encoding='utf-8') as f:
            if inconsistencias:
                f.write("RELATÓRIO DE INCONSISTÊNCIAS ENCONTRADAS\n")
                f.write("========================================\n\n")
                for item in inconsistencias:
                    f.write(f"- {item}\n")
            else:
                f.write("Nenhuma inconsistência encontrada.\n")
            f.write(f"\nDetalhes completos disponíveis no arquivo Excel: {caminho_saida}\n")
    except Exception as e:
        logging.error(f"Erro ao gerar relatório de texto: {e}")

    logging.info("Processamento finalizado.")

if __name__ == "__main__":
    main()
