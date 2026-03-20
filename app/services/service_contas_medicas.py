from datetime import datetime
from time import sleep
import os
import re
from pathlib import Path
from time import sleep
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from app.services.base_browser.browser_factory import BrowserFactory
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from enum import Enum
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
import os

load_dotenv()

DATA_INICIO = "01/01/2026"
DATA_FIM = "31/01/2026"

class ServiceContasMedicas:

    def __init__(self, headless=False):
        self.url = os.getenv('URL_SOC', 'https://sistema.soc.com.br/WebSoc/')
        self._usuario: str = os.getenv('USER_SOC')  # type: ignore
        self._senha: str = os.getenv('PASSWORD_SOC')  # type: ignore
        self._id_login: str = os.getenv('ID_SOC')  # type: ignore
        self.driver = BrowserFactory(headless=headless).get_driver()
        self.wait = WebDriverWait(self.driver, 30)

    def login(self):
        print("Iniciando login...")
        self.driver.get(self.url)

        digitos = [int(d) for d in self._id_login]
        usuario_input = self.driver.find_element(By.ID, "usu")
        senha_input = self.driver.find_element(By.ID, "senha")

        usuario_input.send_keys(self._usuario)
        senha_input.send_keys(self._senha)

        for d in digitos:
            self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@value="{d}"]'))).click()
            sleep(0.2)

        self.driver.find_element(By.ID, "bt_entrar").click()
        sleep(10)

        try:
            modal = self.driver.find_element(By.ID, "modalalertas")
            if modal.is_displayed():
                self.driver.find_element(By.ID, "btn_ok").click()
        except:
            pass

        for xpath in [
            '//html/body/div[2]/div[1]/ul/li[3]/a/img',
            '//html/body/center/h1'
        ]:
            try:
                elem = self.driver.find_element(By.XPATH, xpath)
                if elem.is_displayed():
                    pass
            except:
                pass

        self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "socframe")))

        self.acessar_relatorio_contas_medicas()

    def acessar_relatorio_contas_medicas(self):
        print("Acessando tela de relatório...")

        self.driver.switch_to.default_content()
        wait = WebDriverWait(self.driver, 15)

        for _ in range(3):
            try:
                input_codigo = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="cod_programa"]'))
                )
                input_codigo.click()
                input_codigo.send_keys("1003")
                break
            except StaleElementReferenceException:
                print("")
                sleep(1)
        else:
            raise Exception("")

        btn_programa = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="btn_programa"]'))
        )
        btn_programa.click()

        sleep(7)

        self.configurar_relatorio(DATA_INICIO, DATA_FIM)

    def configurar_relatorio(self, data_inicio: str, data_fim: str):
        print("Configurando relatório...")

        wait = WebDriverWait(self.driver, 20)

        self.driver.switch_to.default_content()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "socframe")))

        inputs = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//fieldset[1]//p[3]//input')
            )
        )

        if len(inputs) < 2:
            raise Exception("Campos de data não encontrados")

        input_inicio, input_fim = inputs[0], inputs[1]

        for campo, valor in [(input_inicio, data_inicio), (input_fim, data_fim)]:
            campo.click()
            campo.send_keys(Keys.CONTROL, "a")
            campo.send_keys(Keys.DELETE)
            campo.send_keys(valor)

        sleep(5)

        self.selecionar_situacoes()

    def selecionar_situacoes(self):
        print("Selecionando situações...")

        wait = WebDriverWait(self.driver, 20)

        self.driver.switch_to.default_content()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "socframe")))

        select_esquerda = wait.until(
            EC.presence_of_element_located((By.ID, "comboSituacao"))
        )

        opcoes = select_esquerda.find_elements(By.TAG_NAME, "option")

        actions = ActionChains(self.driver)
        actions.key_down(Keys.CONTROL)

        for opcao in opcoes:
            value = opcao.get_attribute("value")

            if value == "2":
                continue

            actions.click(opcao)

        actions.key_up(Keys.CONTROL)
        actions.perform()

        btn_associar = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//a[contains(@href,"fassociar")]')
            )
        )
        btn_associar.click()

        sleep(5)
        
        self.selecionar_campos_relatorio()

    def selecionar_campos_relatorio(self):
        print("Selecionando campos do relatório...")

        wait = WebDriverWait(self.driver, 20)

        self.driver.switch_to.default_content()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "socframe")))

        self.driver.execute_script("""
            var origem = document.getElementById('comboCamposRelatorio');
            var destino = document.getElementById('comboCamposSelecionados');

            // pega valores já selecionados (direita)
            var valoresDestino = new Set();
            for (var i = 0; i < destino.options.length; i++) {
                valoresDestino.add(destino.options[i].value);
            }

            // seleciona apenas os que não estão na direita
            for (var i = 0; i < origem.options.length; i++) {
                var opt = origem.options[i];

                if (!valoresDestino.has(opt.value)) {
                    opt.selected = true;
                }
            }

            // executa associação
            fassociar('comboCamposRelatorio','comboCamposSelecionados');
        """)

        sleep(5)
        self.selecionar_campos_inconsistencias()

    def selecionar_campos_inconsistencias(self):
        print("Selecionando campos de inconsistências...")

        wait = WebDriverWait(self.driver, 20)

        self.driver.switch_to.default_content()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "socframe")))

        self.driver.execute_script("""
            var origem = document.getElementById('comboCamposInconsistenciasRelatorio');
            var destino = document.getElementById('comboCamposInconsistenciasSelecionados');

            // pega valores já selecionados (direita)
            var valoresDestino = new Set();
            for (var i = 0; i < destino.options.length; i++) {
                valoresDestino.add(destino.options[i].value);
            }

            // seleciona apenas os que NÃO estão na direita
            for (var i = 0; i < origem.options.length; i++) {
                var opt = origem.options[i];

                if (!valoresDestino.has(opt.value)) {
                    opt.selected = true;
                }
            }

            // executa associação
            fassociar('comboCamposInconsistenciasRelatorio','comboCamposInconsistenciasSelecionados');
        """)

        sleep(5)
        
    def gerar_excel(self):
        print("Clicando em excel...")

        wait = WebDriverWait(self.driver, 20)

        self.driver.switch_to.default_content()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "socframe")))

        self.driver(By.XPATH, "/html/body/div[5]/div/form[1]/age_nao_gravar/div[1]/table/tbody/tr/td[3]/a").click()