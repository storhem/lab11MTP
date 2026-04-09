"""
Тесты валидации docker-compose.yml:
проверяем наличие и корректность лимитов ресурсов (М9).
"""
import re
import pytest
import yaml
from pathlib import Path

COMPOSE_PATH = Path(__file__).parent.parent / "docker-compose.yml"
SERVICES = ["notes-api", "notes-reader"]


@pytest.fixture(scope="module")
def compose():
    with open(COMPOSE_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ── Структура файла ───────────────────────────────────────────────────────────

def test_compose_file_exists():
    assert COMPOSE_PATH.exists(), "docker-compose.yml не найден"


def test_compose_has_services(compose):
    assert "services" in compose


def test_compose_has_volumes(compose):
    assert "volumes" in compose


def test_all_services_present(compose):
    for svc in SERVICES:
        assert svc in compose["services"], f"Сервис {svc} отсутствует"


# ── Наличие блока deploy.resources ────────────────────────────────────────────

@pytest.mark.parametrize("service", SERVICES)
def test_service_has_deploy(compose, service):
    assert "deploy" in compose["services"][service], \
        f"{service}: отсутствует блок deploy"


@pytest.mark.parametrize("service", SERVICES)
def test_service_has_resources(compose, service):
    assert "resources" in compose["services"][service]["deploy"], \
        f"{service}: отсутствует блок resources"


@pytest.mark.parametrize("service", SERVICES)
def test_service_has_limits(compose, service):
    resources = compose["services"][service]["deploy"]["resources"]
    assert "limits" in resources, f"{service}: отсутствует блок limits"


@pytest.mark.parametrize("service", SERVICES)
def test_service_has_reservations(compose, service):
    resources = compose["services"][service]["deploy"]["resources"]
    assert "reservations" in resources, f"{service}: отсутствует блок reservations"


# ── CPU лимиты ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("service", SERVICES)
def test_cpu_limit_present(compose, service):
    limits = compose["services"][service]["deploy"]["resources"]["limits"]
    assert "cpus" in limits, f"{service}: не задан лимит CPU"


@pytest.mark.parametrize("service", SERVICES)
def test_cpu_limit_is_positive(compose, service):
    cpus = float(compose["services"][service]["deploy"]["resources"]["limits"]["cpus"])
    assert cpus > 0, f"{service}: лимит CPU должен быть > 0"


@pytest.mark.parametrize("service", SERVICES)
def test_cpu_limit_reasonable(compose, service):
    cpus = float(compose["services"][service]["deploy"]["resources"]["limits"]["cpus"])
    assert cpus <= 4.0, f"{service}: лимит CPU подозрительно высокий (> 4.0)"


@pytest.mark.parametrize("service", SERVICES)
def test_cpu_reservation_present(compose, service):
    reservations = compose["services"][service]["deploy"]["resources"]["reservations"]
    assert "cpus" in reservations, f"{service}: не задан reservation CPU"


@pytest.mark.parametrize("service", SERVICES)
def test_cpu_reservation_lte_limit(compose, service):
    resources = compose["services"][service]["deploy"]["resources"]
    limit = float(resources["limits"]["cpus"])
    reservation = float(resources["reservations"]["cpus"])
    assert reservation <= limit, \
        f"{service}: reservation CPU ({reservation}) превышает limit ({limit})"


# ── Memory лимиты ─────────────────────────────────────────────────────────────

def parse_memory(value: str) -> int:
    """Парсит строку памяти Docker (256M, 1G, 512m) в байты."""
    value = str(value).strip()
    match = re.fullmatch(r"(\d+(?:\.\d+)?)([KMGkmg]?)", value)
    assert match, f"Неизвестный формат памяти: {value}"
    num, unit = float(match.group(1)), match.group(2).upper()
    multipliers = {"": 1, "K": 1024, "M": 1024**2, "G": 1024**3}
    return int(num * multipliers[unit])


@pytest.mark.parametrize("service", SERVICES)
def test_memory_limit_present(compose, service):
    limits = compose["services"][service]["deploy"]["resources"]["limits"]
    assert "memory" in limits, f"{service}: не задан лимит памяти"


@pytest.mark.parametrize("service", SERVICES)
def test_memory_limit_positive(compose, service):
    mem = parse_memory(compose["services"][service]["deploy"]["resources"]["limits"]["memory"])
    assert mem > 0, f"{service}: лимит памяти должен быть > 0"


@pytest.mark.parametrize("service", SERVICES)
def test_memory_limit_at_least_32mb(compose, service):
    mem = parse_memory(compose["services"][service]["deploy"]["resources"]["limits"]["memory"])
    assert mem >= 32 * 1024**2, f"{service}: лимит памяти слишком мал (< 32M)"


@pytest.mark.parametrize("service", SERVICES)
def test_memory_limit_reasonable(compose, service):
    mem = parse_memory(compose["services"][service]["deploy"]["resources"]["limits"]["memory"])
    assert mem <= 4 * 1024**3, f"{service}: лимит памяти подозрительно высокий (> 4G)"


@pytest.mark.parametrize("service", SERVICES)
def test_memory_reservation_present(compose, service):
    reservations = compose["services"][service]["deploy"]["resources"]["reservations"]
    assert "memory" in reservations, f"{service}: не задан reservation памяти"


@pytest.mark.parametrize("service", SERVICES)
def test_memory_reservation_lte_limit(compose, service):
    resources = compose["services"][service]["deploy"]["resources"]
    limit = parse_memory(resources["limits"]["memory"])
    reservation = parse_memory(resources["reservations"]["memory"])
    assert reservation <= limit, \
        f"{service}: reservation памяти ({reservation}) превышает limit ({limit})"


# ── Логика: reader должен быть скромнее API ───────────────────────────────────

def test_reader_cpu_limit_lte_api(compose):
    api_cpu = float(compose["services"]["notes-api"]["deploy"]["resources"]["limits"]["cpus"])
    reader_cpu = float(compose["services"]["notes-reader"]["deploy"]["resources"]["limits"]["cpus"])
    assert reader_cpu <= api_cpu, \
        "notes-reader не должен иметь больше CPU, чем notes-api"


def test_reader_memory_limit_lte_api(compose):
    api_mem = parse_memory(compose["services"]["notes-api"]["deploy"]["resources"]["limits"]["memory"])
    reader_mem = parse_memory(compose["services"]["notes-reader"]["deploy"]["resources"]["limits"]["memory"])
    assert reader_mem <= api_mem, \
        "notes-reader не должен иметь больше памяти, чем notes-api"
