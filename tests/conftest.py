import pytest
import tempfile
import os
from pathlib import Path
from src.database.connection import init_db
from src.database.repository import RiskRepository
from src.services.mock_saha360 import MockSaha360Service

@pytest.fixture
def temp_repo():
    """Her test için izole, geçici bir SQLite veritabanı sağlar."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_db_path = Path(f.name)
    
    init_db(temp_db_path)
    repo = RiskRepository(db_path=temp_db_path)
    
    yield repo
    
    if temp_db_path.exists():
        os.remove(temp_db_path)

@pytest.fixture
def seeded_repo(temp_repo):
    """Sentetik Saha 360 müşteri verisi yüklenmiş repo."""
    service = MockSaha360Service(temp_repo)
    service.seed_synthetic_clients()
    return temp_repo
