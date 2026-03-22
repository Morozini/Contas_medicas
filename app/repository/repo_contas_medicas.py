from datetime import datetime, time
import pandas as pd
from app.database.models import AnaliseAtendimento, InconsistenciasAtendimento


class ContasMedicasRepository:

    async def limpar_tabelas(self, connection):
        print("Limpando tabelas...")

        await AnaliseAtendimento.all().using_db(connection).delete()
        await InconsistenciasAtendimento.all().using_db(connection).delete()

        print("Tabelas limpas com sucesso!")

    def _to_date(self, value):
        if not value:
            return None
        try:
            return datetime.strptime(str(value), "%d/%m/%Y").date()
        except:
            return None
        
    def _to_time(self, value):
        import pandas as pd
        from datetime import datetime

        if value is None or pd.isna(value):
            return None

        try:
            if isinstance(value, (float, int)):
                total_seconds = int(value * 24 * 60 * 60)
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                return f"{hours:02}:{minutes:02}:{seconds:02}"


            return datetime.strptime(str(value), "%H:%M:%S").strftime("%H:%M:%S")
        except:
            try:
                return datetime.strptime(str(value), "%H:%M").strftime("%H:%M:%S")
            except:
                return None

    def _to_float(self, value):
        if not value:
            return None
        try:
            return float(str(value).replace(",", "."))
        except:
            return None

    async def salvar_analise(self, df, connection):
        objetos = []

        for _, row in df.iterrows():
            objetos.append(
                AnaliseAtendimento(
                    data_inicio_analise=self._to_date(row.get("data_inicio_analise")),
                    matricula_funcionario=row.get("matricula_do_funcionario"),
                    nome_funcionario=row.get("nome_funcionario"),
                    data_realizacao=self._to_date(row.get("data_realizacao")),
                    tipo_exame=row.get("tipo_exame"),
                    exame=row.get("exame"),
                    unidade_funcionario=row.get("unidade_funcionario"),
                    valor_pagar=self._to_float(row.get("valor_pagar")),
                    inconsistencia=row.get("inconsistencia"),
                    status_atendimento=row.get("status_atendimento"),
                    sequencial_ficha=row.get("sequencial_ficha"),
                    sequencial_resultado=row.get("sequencial_resultado"),
                    nome_responsavel_aso=row.get("nome_responsavel_aso"),
                    assinatura_digital_aso=row.get("assinatura_digital_aso"),
                    assinatura_digital_ficha_clinica=row.get("assinatura_digital_ficha_clinica"),
                    atendido_via_socnet=row.get("atendido_via_socnet"),
                    cargo_funcionario=row.get("cargo_do_funcionario"),
                    cidade_prestador=row.get("cidade_prestador"),
                    classificacao_socged=row.get("classificacao_socged"),
                    cliente_socnet=row.get("cliente_socnet"),
                    cnpj_empresa=row.get("cnpj_empresa"),
                    cnpj_cpf_prestador=row.get("cnpj_cpf_do_prestador"),
                    cobranca_ficha_clinica=row.get("cobranca_ficha_clinica"),
                    codigo_empresa=row.get("codigo_da_empresa"),
                    codigo_exame=row.get("codigo_exame"),
                    codigo_exame_socnet=row.get("codigo_do_exame_mapeado_socnet"),
                    codigo_funcionario=row.get("codigo_funcionario"),
                    codigo_prestador=row.get("codigo_prestador"),
                    codigo_ged_aso=row.get("codigo_ged_aso"),
                    codigo_ged_consulta=row.get("codigo_ged_consulta"),
                    codigo_ged_ficha=row.get("codigo_ged_ficha"),
                    codigo_ged_resultado=row.get("codigo_ged_resultado"),
                    conselho_classe_responsavel_aso=row.get("conselho_de_classe_do_responsavel_aso"),
                    cpf_funcionario=row.get("cpf_funcionario"),
                    data_criacao_ficha=self._to_date(row.get("data_criacao_da_ficha")),
                    data_contagem=self._to_date(row.get("data_da_contagem")),
                    data_ficha=self._to_date(row.get("data_da_ficha")),
                    data_ultima_alteracao_resultado=self._to_date(row.get("data_da_ultima_alteracao_do_resultado")),
                    data_emissao_documento_fiscal=self._to_date(row.get("data_de_emissao_do_documento_fiscal")),
                    data_liberacao=self._to_date(row.get("data_de_liberacao")),
                    data_postagem=self._to_date(row.get("data_de_postagem")),
                    data_recebimento=self._to_date(row.get("data_de_recebimento")),
                    data_upload_ged_aso=self._to_date(row.get("data_do_upload_ged_aso")),
                    data_upload_ged_consulta=self._to_date(row.get("data_do_upload_ged_consulta")),
                    data_upload_ged_ficha=self._to_date(row.get("data_do_upload_ged_ficha")),
                    data_upload_ged_resultado=self._to_date(row.get("data_do_upload_ged_resultado")),
                    data_emissao_aso=self._to_date(row.get("data_emissao_do_aso")),
                    data_ultima_alteracao=self._to_date(row.get("data_ultima_alteracao")),
                    empresa_funcionario=row.get("empresa_funcionario"),
                    estado_prestador=row.get("estado_do_prestador"),
                    matricula_rh_funcionario=row.get("matricula_rh_do_funcionario"),
                    nome_banco=row.get("nome_do_banco"),
                    nome_lote=row.get("nome_do_lote"),
                    nome_prestador=row.get("nome_do_prestador"),
                    numero_documento_fiscal=row.get("numero_do_documento_fiscal"),
                    prestador_socnet=row.get("prestador_socnet"),
                    setor_funcionario=row.get("setor_do_funcionario"),
                    situacao_empresa=row.get("situacao_da_empresa"),
                    tipo_pagamento=row.get("tipo_de_pagamento"),
                    tipo_pessoa=row.get("tipo_pessoa"),
                    uf_conselho_classe_responsavel_aso=row.get("uf_conselho_de_classe_responsavel_aso"),
                    usuario_ultima_alteracao=row.get("usuario_ultima_alteracao"),
                    valor_documento_fiscal=self._to_float(row.get("valor_do_documento_fiscal")),
                )
            )

        await AnaliseAtendimento.bulk_create(objetos, batch_size=500, using_db=connection)

    async def salvar_inconsistencias(self, df, connection):
        objetos = []

        for _, row in df.iterrows():
            objetos.append(
                InconsistenciasAtendimento(
                    nome_funcionario=row.get("nome_funcionario"),
                    exame=row.get("exame"),
                    inconsistencia=row.get("inconsistencia"),
                    observacao_cliente=row.get("observacao_do_cliente"),
                    status_inconsistencia=row.get("status_da_inconsistencia"),
                    codigo_exame=row.get("codigo_exame"),
                    cpf_funcionario=row.get("cpf_funcionario"),
                    data_observacao_cliente=self._to_date(row.get("data_da_observacao_do_cliente")),
                    data_observacao_prestador=self._to_date(row.get("data_da_observacao_do_prestador")),
                    empresa_funcionario=row.get("empresa_funcionario"),
                    hora_observacao_cliente=self._to_time(row.get("hora_da_observacao_do_cliente")),
                    hora_observacao_prestador=self._to_time(row.get("hora_da_observacao_do_prestador")),
                    observacao_prestador=row.get("observacao_do_prestador"),
                )
            )

        await InconsistenciasAtendimento.bulk_create(objetos, batch_size=500, using_db=connection)