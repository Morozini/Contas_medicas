import zipfile
import pandas as pd
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import re

class TransformationData:
    
    def __init__(self, zip_path, type_excel, number_row_del: int):
        self.zip_path = Path(zip_path)
        self.cleaned_data = None
        self.type_excel = type_excel
        self.number_row_del = number_row_del
    
    def read_zip_path(self, sheet_name):
        with TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)
                xlsx_files = list(Path(tmpdir).glob(f'*.{self.type_excel}'))
                if not xlsx_files:
                    raise FileNotFoundError("Nenhum arquivo encontrado no ZIP.")
                
                excel_path = xlsx_files[0]

                padrao = re.compile(rf"^{re.escape(sheet_name)}(?:\s\d+)?$")
                todos_dfs = []

                engine = "openpyxl" if self.type_excel == "xlsx" else "xlrd"
                
                with pd.ExcelFile(excel_path, engine=engine) as xls:
                    abas_filtradas = [aba for aba in xls.sheet_names if padrao.match(aba)] # type: ignore
                    if not abas_filtradas:
                        raise ValueError(f"Nenhuma aba encontrada com o padrão '{sheet_name}'")
                    
                    for aba in abas_filtradas:
                        df = pd.read_excel(xls, sheet_name=aba, header=None)
                        df.columns = df.iloc[self.number_row_del]
                        number_row_del = int(self.number_row_del) + 1
                        df = df.iloc[number_row_del:].reset_index(drop=True)
                        todos_dfs.append(df)

                self.cleaned_data = pd.concat(todos_dfs, ignore_index=True)

    def load_data_content(self):
        if self.cleaned_data is None:
            raise ValueError("Dados ainda não carregados.")
        pass

    def _load_path_content(self, output_path: Path):
        path_name = Path(output_path)
        
        if not os.path.exists(path_name):
            os.makedirs(path_name)
        
        return path_name

    def export_clean_excel(self, output_path):
        
        new_path = self._load_path_content(output_path)
        
        if self.cleaned_data is None:
            raise ValueError("Dados ainda não carregados.")
        
        from openpyxl import Workbook
        from openpyxl.utils.dataframe import dataframe_to_rows
        
        wb = Workbook()
        ws = wb.active

        for row in dataframe_to_rows(self.cleaned_data, index=False, header=True):
            ws.append(row) # type: ignore
        
        new_name = self.zip_path.name.replace('.zip', '.xlsx')
        file_name = Path(new_path) / new_name
        
        wb.save(file_name)