import json
import sqlite3
from typing import List, Optional, Dict, Any
from src.database.connection import get_connection
from src.models.client import Client
from src.models.inspection import Inspection, InspectionPhoto
from src.models.recommendation import Recommendation

class RiskRepository:
    def __init__(self, db_path=None):
        self.db_path = db_path

    def _get_conn(self) -> sqlite3.Connection:
        return get_connection(self.db_path)

    # ================= Müşteri (Client) İşlemleri =================
    def add_client(self, client: Client) -> int:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO clients (synthetic_code, company_name, sector, city, district, address, insured_value, hazard_class)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(synthetic_code) DO UPDATE SET
                    company_name=excluded.company_name,
                    sector=excluded.sector,
                    city=excluded.city,
                    district=excluded.district,
                    address=excluded.address,
                    insured_value=excluded.insured_value,
                    hazard_class=excluded.hazard_class
                """,
                (client.synthetic_code, client.company_name, client.sector, client.city, client.district,
                 client.address, client.insured_value, client.hazard_class)
            )
            client_id = cursor.lastrowid
            if not client_id or client_id == 0:
                row = cursor.execute("SELECT id FROM clients WHERE synthetic_code = ?", (client.synthetic_code,)).fetchone()
                client_id = row["id"] if row else 0
            return client_id

    def get_client_by_id(self, client_id: int) -> Optional[Client]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
            if not row:
                return None
            return Client(
                id=row["id"],
                synthetic_code=row["synthetic_code"],
                company_name=row["company_name"],
                sector=row["sector"],
                city=row["city"],
                district=row["district"],
                address=row["address"] or "",
                insured_value=row["insured_value"],
                hazard_class=row["hazard_class"]
            )

    def get_all_clients(self) -> List[Client]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM clients ORDER BY company_name ASC").fetchall()
            return [
                Client(
                    id=r["id"],
                    synthetic_code=r["synthetic_code"],
                    company_name=r["company_name"],
                    sector=r["sector"],
                    city=r["city"],
                    district=r["district"],
                    address=r["address"] or "",
                    insured_value=r["insured_value"],
                    hazard_class=r["hazard_class"]
                ) for r in rows
            ]

    # ================= Teftiş (Inspection) İşlemleri =================
    def create_inspection(self, insp: Inspection) -> int:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO inspections (
                    client_id, inspector_name, inspection_date, occupancy_type,
                    building_construction, total_area_sqm, number_of_floors,
                    fire_measures, security_measures, natural_hazard_measures,
                    calculated_risk_score, risk_level, ai_executive_summary,
                    ai_recommendations, uw_notes, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    insp.client_id, insp.inspector_name, insp.inspection_date,
                    insp.occupancy_type, insp.building_construction,
                    insp.total_area_sqm, insp.number_of_floors,
                    json.dumps(insp.fire_measures, ensure_ascii=False),
                    json.dumps(insp.security_measures, ensure_ascii=False),
                    json.dumps(insp.natural_hazard_measures, ensure_ascii=False),
                    insp.calculated_risk_score, insp.risk_level,
                    insp.ai_executive_summary, insp.ai_recommendations,
                    insp.uw_notes, insp.status
                )
            )
            return cursor.lastrowid

    def update_inspection(self, insp: Inspection) -> bool:
        if not insp.id:
            return False
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE inspections SET
                    inspector_name = ?,
                    inspection_date = ?,
                    occupancy_type = ?,
                    building_construction = ?,
                    total_area_sqm = ?,
                    number_of_floors = ?,
                    fire_measures = ?,
                    security_measures = ?,
                    natural_hazard_measures = ?,
                    calculated_risk_score = ?,
                    risk_level = ?,
                    ai_executive_summary = ?,
                    ai_recommendations = ?,
                    uw_notes = ?,
                    status = ?
                WHERE id = ?
                """,
                (
                    insp.inspector_name, insp.inspection_date,
                    insp.occupancy_type, insp.building_construction,
                    insp.total_area_sqm, insp.number_of_floors,
                    json.dumps(insp.fire_measures, ensure_ascii=False),
                    json.dumps(insp.security_measures, ensure_ascii=False),
                    json.dumps(insp.natural_hazard_measures, ensure_ascii=False),
                    insp.calculated_risk_score, insp.risk_level,
                    insp.ai_executive_summary, insp.ai_recommendations,
                    insp.uw_notes, insp.status,
                    insp.id
                )
            )
            return cursor.rowcount > 0

    def get_inspection_by_id(self, inspection_id: int) -> Optional[Inspection]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM inspections WHERE id = ?", (inspection_id,)).fetchone()
            if not row:
                return None
            insp = self._row_to_inspection(row)
            insp.photos = self.get_photos_for_inspection(inspection_id)
            return insp

    def get_all_inspections(self) -> List[Inspection]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM inspections ORDER BY id DESC").fetchall()
            return [self._row_to_inspection(r) for r in rows]

    def _row_to_inspection(self, row: sqlite3.Row) -> Inspection:
        return Inspection(
            id=row["id"],
            client_id=row["client_id"],
            inspector_name=row["inspector_name"],
            inspection_date=row["inspection_date"],
            occupancy_type=row["occupancy_type"] or "",
            building_construction=row["building_construction"] or "",
            total_area_sqm=row["total_area_sqm"] or 0.0,
            number_of_floors=row["number_of_floors"] or 1,
            fire_measures=json.loads(row["fire_measures"]) if row["fire_measures"] else {},
            security_measures=json.loads(row["security_measures"]) if row["security_measures"] else {},
            natural_hazard_measures=json.loads(row["natural_hazard_measures"]) if row["natural_hazard_measures"] else {},
            calculated_risk_score=row["calculated_risk_score"] or 0.0,
            risk_level=row["risk_level"] or "",
            ai_executive_summary=row["ai_executive_summary"] or "",
            ai_recommendations=row["ai_recommendations"] or "",
            uw_notes=row["uw_notes"] or "",
            status=row["status"] or "Taslak",
            created_at=str(row["created_at"]) if "created_at" in row.keys() else ""
        )

    # ================= Fotoğraf (Photos) İşlemleri =================
    def add_photo(self, photo: InspectionPhoto) -> int:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO inspection_photos (inspection_id, file_path, category, caption)
                VALUES (?, ?, ?, ?)
                """,
                (photo.inspection_id, photo.file_path, photo.category, photo.caption)
            )
            return cursor.lastrowid

    def get_photos_for_inspection(self, inspection_id: int) -> List[InspectionPhoto]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM inspection_photos WHERE inspection_id = ? ORDER BY id ASC", (inspection_id,)).fetchall()
            return [
                InspectionPhoto(
                    id=r["id"],
                    inspection_id=r["inspection_id"],
                    file_path=r["file_path"],
                    category=r["category"],
                    caption=r["caption"] or "",
                    uploaded_at=str(r["uploaded_at"])
                ) for r in rows
            ]

    # ================= Öneri (Recommendations) İşlemleri =================
    def add_recommendation(self, rec: Recommendation) -> int:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO recommendations (inspection_id, priority, category, finding, action_required, target_deadline_days, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (rec.inspection_id, rec.priority, rec.category, rec.finding, rec.action_required, rec.target_deadline_days, rec.status)
            )
            return cursor.lastrowid

    def get_recommendations_for_inspection(self, inspection_id: int) -> List[Recommendation]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM recommendations WHERE inspection_id = ? ORDER BY id ASC", (inspection_id,)).fetchall()
            return [
                Recommendation(
                    id=r["id"],
                    inspection_id=r["inspection_id"],
                    priority=r["priority"],
                    category=r["category"],
                    finding=r["finding"],
                    action_required=r["action_required"],
                    target_deadline_days=r["target_deadline_days"],
                    status=r["status"],
                    created_at=str(r["created_at"])
                ) for r in rows
            ]

    def update_recommendation_status(self, rec_id: int, status: str) -> bool:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE recommendations SET status = ? WHERE id = ?", (status, rec_id))
            return cursor.rowcount > 0

    def get_all_recommendations(self) -> List[Recommendation]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM recommendations ORDER BY id DESC").fetchall()
            return [
                Recommendation(
                    id=r["id"],
                    inspection_id=r["inspection_id"],
                    priority=r["priority"],
                    category=r["category"],
                    finding=r["finding"],
                    action_required=r["action_required"],
                    target_deadline_days=r["target_deadline_days"],
                    status=r["status"],
                    created_at=str(r["created_at"])
                ) for r in rows
            ]
