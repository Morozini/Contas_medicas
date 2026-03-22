import asyncio
from app.services.service_contas_medicas import ServiceContasMedicas
from app.database.models import AnaliseAtendimento, InconsistenciasAtendimento


class ProcessarContasMedicasUseCase:

    def __init__(self):
        self.service = ServiceContasMedicas(headless=True)

    async def execute(self):
        try:
            self.service.login()

            data = self.service.get_processed_data()

            analise_df = data["analise"]
            inconsistencias_df = data["inconsistencias"]

            await self._salvar_analise(analise_df)
            await self._salvar_inconsistencias(inconsistencias_df)

            print("Processo finalizado com sucesso!")

        finally:
            self.service.close()

    async def _salvar_analise(self, df):
        objetos = []

        for _, row in df.iterrows():
            objetos.append(
                AnaliseAtendimento(
                    nome_funcionario=row.get("Nome Funcionário"),
                    exame=row.get("Exame"),
                    cpf_funcionario=row.get("CPF do Funcionário"),
                )
            )

        await AnaliseAtendimento.bulk_create(objetos, batch_size=500)

    async def _salvar_inconsistencias(self, df):
        objetos = []

        for _, row in df.iterrows():
            objetos.append(
                InconsistenciasAtendimento(
                    nome_funcionario=row.get("Nome Funcionário"),
                    exame=row.get("Exame"),
                    inconsistencia=row.get("Inconsistência"),
                    cpf_funcionario=row.get("CPF do Funcionário"),
                )
            )

        await InconsistenciasAtendimento.bulk_create(objetos, batch_size=500)