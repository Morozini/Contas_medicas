import asyncio
from pathlib import Path

from app.database.config import init, close
from app.data_processing.transformers import TransformationData
from app.repository.repo_contas_medicas import ContasMedicasRepository
from tortoise.transactions import in_transaction

ZIP_PATH = Path("C:/Users/Gabriel/Desktop/contas_medicas/downloads/2504442351774054137112.zip")


async def main():
    await init()

    print("Processando arquivo local...")

    transformer = TransformationData(
        zip_path=str(ZIP_PATH),
        type_excel='xlsx',
        number_row_del=2
    )

    analise_df = transformer.read_zip_path("Análise de Atendimentos")
    inconsistencias_df = transformer.read_zip_path("Inconsistencias de Atendimentos")

    print(f"Analise: {len(analise_df)} registros")
    print(f"Inconsistencias: {len(inconsistencias_df)} registros")

    repo = ContasMedicasRepository()

    async with in_transaction() as connection:
        await repo.limpar_tabelas(connection)
        await repo.salvar_analise(analise_df, connection)
        await repo.salvar_inconsistencias(inconsistencias_df, connection)

    print("Dados inseridos com sucesso!")

    await close()


if __name__ == "__main__":
    asyncio.run(main())