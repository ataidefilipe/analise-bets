"""
tests/test_notebooks.py
-----------------------
Testes automatizados de validação estrutural e integridade dos cadernos Jupyter (Fase 9):
1. Confirma existência dos 4 cadernos em notebooks/.
2. Valida conformidade com o schema oficial nbformat v4.
3. Garante presença balanceada de células Markdown e Code.
4. Verifica ausência de erros de sintaxe nos blocos de código dos cadernos.
"""

import os
import pytest
import nbformat

NOTEBOOKS_DIR = "notebooks"
EXPECTED_NOTEBOOKS = [
    "01_pipeline_dados_e_limpeza.ipynb",
    "02_analise_exploratoria_e_paradoxo_disciplinar.ipynb",
    "03_modelagem_econometrica_painel_did.ipynb",
    "04_sistema_triagem_anomalias_integridade.ipynb",
]


@pytest.mark.parametrize("nb_filename", EXPECTED_NOTEBOOKS)
def test_notebook_exists_and_valid_schema(nb_filename):
    """Valida se o notebook existe e cumpre as diretrizes do schema nbformat v4."""
    nb_path = os.path.join(NOTEBOOKS_DIR, nb_filename)
    assert os.path.exists(nb_path), f"Caderno ausente: {nb_path}"

    with open(nb_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    # Validar schema oficial
    nbformat.validate(nb)

    # Verificar presença de células
    assert len(nb.cells) >= 8, f"Caderno {nb_filename} possui poucas células ({len(nb.cells)})"

    md_cells = [c for c in nb.cells if c.cell_type == "markdown"]
    code_cells = [c for c in nb.cells if c.cell_type == "code"]

    assert len(md_cells) >= 4, f"Caderno {nb_filename} possui documentação Markdown insuficiente"
    assert len(code_cells) >= 4, f"Caderno {nb_filename} possui poucos blocos de código executáveis"


@pytest.mark.parametrize("nb_filename", EXPECTED_NOTEBOOKS)
def test_notebook_code_cells_syntax(nb_filename):
    """Testa se todo o código Python embutido no caderno compila sem SyntaxError."""
    nb_path = os.path.join(NOTEBOOKS_DIR, nb_filename)
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    for idx, cell in enumerate(nb.cells):
        if cell.cell_type == "code":
            try:
                compile(cell.source, f"{nb_filename}_cell_{idx}", "exec")
            except SyntaxError as e:
                pytest.fail(f"Erro de sintaxe em {nb_filename} célula {idx}: {e}")
