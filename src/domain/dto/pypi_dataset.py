from pydantic import BaseModel


class PypiDataset(BaseModel):
    download_id: int
    download_timestamp: int
    country_code: str
    pypi_project_id: str
    pypi_package_version: str
    installer_name: str
    python_version: str
