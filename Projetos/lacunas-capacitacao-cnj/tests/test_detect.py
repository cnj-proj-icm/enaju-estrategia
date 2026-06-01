import yaml

from pipeline.common import ProjectPaths
from pipeline.detect import evaluate_segment


def _criteria():
    root = ProjectPaths.discover().root
    return yaml.safe_load((root / "config" / "criterios_analiticos.yml").read_text(encoding="utf-8"))


def test_score_is_deterministic_for_explicit_gap() -> None:
    result = evaluate_segment(
        "Ha necessidade de capacitacao para aprimorar o saneamento de dados no DataJud.",
        _criteria(),
    )
    assert result["tipo_gap"] == "explicito"
    assert result["score"] >= 9
    assert "dados_e_tecnologia" in result["eixos"]
    assert result["hipotese_competencia"] == "governanca e qualidade de dados"


def test_organizational_signal_is_implicit_gap() -> None:
    result = evaluate_segment("Observou-se baixa adesao e ausencia de protocolo.", _criteria())
    assert result["tipo_gap"] in {"explicito", "implicito"}


def test_information_is_not_training_and_disability_is_not_deficiency() -> None:
    result = evaluate_segment(
        "A informação deve ser acessível para pessoas com deficiência.",
        _criteria(),
    )
    assert "formacao" not in result["termos_encontrados"]
    assert "deficiencia" not in result["termos_encontrados"]
