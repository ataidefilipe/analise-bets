"""
Testes automatizados para a Apresentação HTML do Projeto
Arquivo alvo: reports/apresentacao_processo_projeto.html
"""

import re
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"
HTML_PATH = REPORTS_DIR / "apresentacao_processo_projeto.html"


def test_html_file_exists():
    assert HTML_PATH.exists(), f"O arquivo {HTML_PATH} não foi encontrado."
    assert HTML_PATH.stat().st_size > 50_000, "O arquivo HTML está inesperadamente pequeno."


def test_images_referenced_exist():
    content = HTML_PATH.read_text(encoding="utf-8")
    
    # Encontrar todas as tags <img src="...">
    img_srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    
    # Filtrar apenas imagens locais
    local_imgs = [src for src in img_srcs if not src.startswith("http") and not src.startswith("data:")]
    
    assert len(local_imgs) >= 15, f"Esperava-se pelo menos 15 imagens locais, encontradas {len(local_imgs)}."
    
    for src in local_imgs:
        img_path = REPORTS_DIR / src
        assert img_path.exists(), f"Imagem referenciada não existe: {img_path}"


def test_governance_and_agent_md_content():
    content = HTML_PATH.read_text(encoding="utf-8")
    
    assert ".agent.md" in content, "Falta menção ao .agent.md"
    assert "Fatos" in content and "Hipóteses" in content and "Resultados" in content and "Decisões" in content
    assert "Causalidade" in content or "causalidade" in content
    assert "Pushback Analítico" in content
    assert "Checklist Final" in content


def test_decisions_matrix_content():
    content = HTML_PATH.read_text(encoding="utf-8")
    
    # Verificar códigos de decisões estratégicas, analíticas e técnicas
    expected_codes = ["D-EST-01", "D-EST-02", "D-EST-07", "D-EST-08", "D-ANA-01", "D-ANA-05", "D-ANA-11", "D-TEC-01", "D-TEC-06"]
    for code in expected_codes:
        assert code in content, f"Código de decisão ausente: {code}"


def test_ground_truth_penalidade_maxima():
    content = HTML_PATH.read_text(encoding="utf-8")
    
    assert "Penalidade Máxima" in content
    assert "Gabriel Tota" in content or "Paulo Miranda" in content or "Nino Paraíba" in content
    assert "100%" in content or "sensibilidade" in content.lower()


def test_non_technical_pedagogical_content():
    content = HTML_PATH.read_text(encoding="utf-8")
    
    # Verificar a existência dos blocos pedagógicos
    assert "Dicionário Express do Leitor Não Técnico" in content
    assert "how-to-read-box" in content
    assert "formula-box" in content
    assert "guide-box" in content
    
    # Verificar analogias fundamentais para leigos
    assert "termômetro do acaso" in content.lower()
    assert "moeda viciada" in content.lower()
    assert "raio-x" in content.lower() or "scanner" in content.lower()
    assert "como ler" in content.lower() or "como interpretar" in content.lower()

