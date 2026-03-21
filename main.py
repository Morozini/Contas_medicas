
from app.services.service_contas_medicas import ServiceContasMedicas


if __name__ == "__main__":
    service = ServiceContasMedicas(headless=False).login()
