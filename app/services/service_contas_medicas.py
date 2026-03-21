from datetime import datetime
from time import sleep
import os
import time
from pathlib import Path
import zipfile
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from app.data_processing.transformers import TransformationData
from app.services.base_browser.browser_factory import BrowserFactory
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from app.utils.get_file import get_latest_file

load_dotenv()

DATA_INICIO = "01/01/2026"
DATA_FIM = "31/01/2026"


class ServiceContasMedicas:

    def __init__(self, headless=False):
        self.url = os.getenv('URL_SOC', 'https://sistema.soc.com.br/WebSoc/')
        self._usuario = os.getenv('USER_SOC')
        self._senha = os.getenv('PASSWORD_SOC')
        self._id_login = os.getenv('ID_SOC')

        self.driver = BrowserFactory(headless=headless).get_driver()
        self.wait = WebDriverWait(self.driver, 30)

        self.zip_path = Path(os.getenv("DOWNLOAD_PATH", "downloads"))
        self.zip_path.mkdir(parents=True, exist_ok=True)

        # Limpa arquivos antigos
        for f in self.zip_path.glob("*"):
            try:
                f.unlink()
            except:
                pass

    def login(self):
        print("Iniciando login...")
        self.driver.get(self.url)

        digitos = [int(d) for d in self._id_login]

        self.driver.find_element(By.ID, "usu").send_keys(self._usuario)
        self.driver.find_element(By.ID, "senha").send_keys(self._senha)

        for d in digitos:
            self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@value="{d}"]'))).click()
            sleep(0.2)

        self.driver.find_element(By.ID, "bt_entrar").click()
        sleep(8)

        try:
            modal = self.driver.find_element(By.ID, "modalalertas")
            if modal.is_displayed():
                self.driver.find_element(By.ID, "btn_ok").click()
        except:
            pass

        self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "socframe")))

        self.acessar_relatorio_contas_medicas()

    def acessar_relatorio_contas_medicas(self):
        print("Acessando tela de relatório...")
        self.driver.switch_to.default_content()
        wait = WebDriverWait(self.driver, 15)

        input_codigo = wait.until(EC.element_to_be_clickable((By.ID, "cod_programa")))
        input_codigo.click()
        input_codigo.send_keys("1003")
        wait.until(EC.element_to_be_clickable((By.ID, "btn_programa"))).click()

        sleep(5)
        self.configurar_relatorio(DATA_INICIO, DATA_FIM)

    def configurar_relatorio(self, data_inicio, data_fim):
        print("Configurando relatório...")
        self.driver.switch_to.default_content()
        self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "socframe")))

        inputs = self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//fieldset[1]//p[3]//input'))
        )
        input_inicio, input_fim = inputs[0], inputs[1]

        for campo, valor in [(input_inicio, data_inicio), (input_fim, data_fim)]:
            campo.click()
            campo.send_keys(Keys.CONTROL, "a")
            campo.send_keys(Keys.DELETE)
            campo.send_keys(valor)

        sleep(2)
        self.selecionar_situacoes()

    def selecionar_situacoes(self):
        print("Selecionando situações...")
        self.driver.switch_to.default_content()
        self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "socframe")))

        select = self.wait.until(EC.presence_of_element_located((By.ID, "comboSituacao")))
        opcoes = select.find_elements(By.TAG_NAME, "option")

        actions = ActionChains(self.driver).key_down(Keys.CONTROL)
        for opcao in opcoes:
            if opcao.get_attribute("value") != "2":
                actions.click(opcao)
        actions.key_up(Keys.CONTROL).perform()

        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@href,"fassociar")]'))).click()
        sleep(2)
        self.selecionar_campos_relatorio()

    def selecionar_campos_relatorio(self):
        print("Selecionando campos do relatório...")
        self.driver.execute_script("""
            var origem = document.getElementById('comboCamposRelatorio');
            var destino = document.getElementById('comboCamposSelecionados');
            var valoresDestino = new Set([...destino.options].map(o => o.value));
            for (var opt of origem.options) {
                if (!valoresDestino.has(opt.value)) opt.selected = true;
            }
            fassociar('comboCamposRelatorio','comboCamposSelecionados');
        """)
        sleep(2)
        self.selecionar_campos_inconsistencias()

    def selecionar_campos_inconsistencias(self):
        print("Selecionando campos de inconsistências...")
        self.driver.execute_script("""
            var origem = document.getElementById('comboCamposInconsistenciasRelatorio');
            var destino = document.getElementById('comboCamposInconsistenciasSelecionados');
            var valoresDestino = new Set([...destino.options].map(o => o.value));
            for (var opt of origem.options) {
                if (!valoresDestino.has(opt.value)) opt.selected = true;
            }
            fassociar('comboCamposInconsistenciasRelatorio','comboCamposInconsistenciasSelecionados');
        """)
        sleep(2)
        self.gerar_excel()

    def gerar_excel(self):
        print("Clicando em excel...")
        self.driver.switch_to.default_content()
        self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "socframe")))

        self.clicar("//a[contains(@href, 'gerarPedidoProcessamento')]")
        codigo = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@id='pedProc']//b")))
        self.codigo_processamento = codigo.text.strip()
        print(f"Codigo gerado para processamento: {self.codigo_processamento}")

        self.clicar("//div[@id='pedProc']//a[contains(., 'Consultar')]")
        self.processar_download()

    def clicar(self, xpath):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()

    def processar_download(self):
        download_xpath = f'//*[@id="{self.codigo_processamento}-download"]/span[1]/a'
        refresh_xpath = '//*[@id="socContent"]//a/img'

        while True:
            try:
                self.clicar(refresh_xpath)
                if self.wait_download_link(download_xpath):
                    self.clicar(download_xpath)
                    print("Download iniciado...")
                    self.esperar_download_finalizar()
                    break
            except TimeoutException:
                continue

        self.get_file_in_zip()

    def wait_download_link(self, xpath):
        try:
            el = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, xpath)))
            return el.text.strip() == "Download"
        except:
            return False

    def esperar_download_finalizar(self, timeout=60):
        print("Aguardando download finalizar...")
        inicio = time.time()

        while time.time() - inicio < timeout:
            arquivos = list(self.zip_path.glob("*"))
            if any(str(f).endswith(".crdownload") for f in arquivos):
                sleep(1)
                continue
            zips = list(self.zip_path.glob("*.zip"))
            if zips:
                print("Download finalizado.")
                return
            sleep(1)
        raise TimeoutError("Download não finalizou.")

    def get_file_in_zip(self, sheet_name=None):
        zip_file = get_latest_file(self.zip_path, "zip")
        print(f"Lendo ZIP: {zip_file}")

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            arquivos = zip_ref.namelist()
            if not arquivos:
                raise Exception("ZIP está vazio.")

            print("Arquivos dentro do ZIP:")
            for a in arquivos:
                print(f" - {a}")

            # Pega primeiro arquivo válido
            arquivo_excel = next((n for n in arquivos if n.endswith((".xls", ".xlsx", ".csv"))), None)
            if not arquivo_excel:
                raise Exception("Nenhum arquivo Excel encontrado dentro do ZIP.")

            # Extrai
            extract_path = self.zip_path / "content"
            extract_path.mkdir(exist_ok=True)
            zip_ref.extractall(extract_path)
            caminho_arquivo = extract_path / arquivo_excel

        print(f"Arquivo encontrado: {caminho_arquivo}")

        transformer = TransformationData(
            zip_path=str(zip_file),  # .zip baixado
            type_excel='xlsx',
            number_row_del=2
        )

        transformer.read_zip_path(sheet_name=None)
        transformer.load_data_content()
        transformer.export_clean_excel(extract_path)
        print(f"Arquivo processado com sucesso: {caminho_arquivo}")

    def close(self):
        self.driver.quit()