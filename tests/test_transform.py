from observatorio.transform import (
    cabecera, es_tech, habilidades, parse_experiencia, parse_lugar, parse_modalidad, parse_nivel, parse_salario,
)

DESC = ("Descripción de la oferta \r\n $ 2.500.000,00 (Mensual) \r\n Contrato a término fijo \r\n"
        " Tiempo Completo \r\n Presencial y remoto \r\n Buscamos analista con Python y SQL.\n"
        "Requerimientos\n Educación mínima: Universidad / Carrera tecnológica\n 2 años de experiencia\n")


def test_salario_se_convierte_a_numero():
    assert parse_salario(cabecera(DESC)) == 2_500_000


def test_salario_a_convenir_es_nulo():
    assert parse_salario(["A convenir", "Contrato a término fijo"]) is None


def test_modalidades():
    assert parse_modalidad(cabecera(DESC)) == "Híbrido"
    assert parse_modalidad(["Remoto"]) == "Remoto"
    assert parse_modalidad(["Tiempo Completo"]) == "Presencial"


def test_experiencia():
    assert parse_experiencia(DESC) == 2
    assert parse_experiencia("sin requisitos") is None


def test_lugar_con_guion_en_el_nombre_de_empresa():
    assert parse_lugar("Data-Tech SAS - Bucaramanga, Santander") == ("Data-Tech SAS", "Bucaramanga", "Santander")


def test_nivel():
    assert parse_nivel("Practicante de sistemas", "") == "Práctica"
    assert parse_nivel("Desarrollador Senior Java", "") == "Senior"
    assert parse_nivel("Desarrollador Jr", "") == "Junior"


def test_habilidades_no_confunde_java_con_javascript():
    assert habilidades("Experiencia en JavaScript y React") == ["JavaScript", "React"]
    assert "Java" in habilidades("Backend en Java y SQL")


def test_es_tech():
    assert es_tech("Desarrollador Full Stack Junior")
    assert es_tech("Analista de Datos")
    assert not es_tech("Estudiante técnico en enfermería")


def test_cabecera_con_saltos_simples_no_incluye_el_cuerpo():
    desc = ("Descripción de la oferta \r\n $ 2.200.000,00 (Mensual)\n Contrato a término indefinido\n"
            " Tiempo Completo\n ESTA ES TU GRAN OPORTUNIDAD, trabajo remoto!!\n")
    cab = cabecera(desc)
    assert cab == ["$ 2.200.000,00 (Mensual)", "Contrato a término indefinido", "Tiempo Completo"]
    assert parse_modalidad(cab) == "Presencial"      # el "remoto" del cuerpo no cuenta
