from sqlalchemy.orm import Session
from models.models import Appointment, Patient, AppointmentStatus
from schemas.schemas import ReportsData, ReportStats
from services.ml_services import calculate_patient_risk

def generate_report(db: Session, psychologist_id: int) -> ReportsData:
    try:
        print(f"🧩 [REPORT] Iniciando relatório do psicólogo {psychologist_id}")

        # Buscar dados no banco
        appointments = db.query(Appointment).filter(Appointment.psychologist_id == psychologist_id).all()
        patients = db.query(Patient).filter(Patient.psychologist_id == psychologist_id).all()

        print(f"   • Agendamentos encontrados: {len(appointments)}")
        print(f"   • Pacientes encontrados: {len(patients)}")

        # Contagens básicas
        total_sessions = len(appointments)
        completed_sessions = len([a for a in appointments if a.status == AppointmentStatus.CONCLUIDO])
        canceled_sessions = len([a for a in appointments if a.status == AppointmentStatus.CANCELADO])
        scheduled_sessions = len([a for a in appointments if a.status == AppointmentStatus.AGENDADO])

        print(f"   • Sessões: {total_sessions}")
        print(f"   • Concluídas: {completed_sessions}")
        print(f"   • Canceladas: {canceled_sessions}")
        print(f"   • Agendadas: {scheduled_sessions}")

        # Calcular taxa de comparecimento
        valid_sessions = completed_sessions + canceled_sessions
        attendance_rate = (completed_sessions / valid_sessions * 100) if valid_sessions > 0 else 0

        # Análise de risco via ML
        ml_risk_analysis = calculate_patient_risk(db, psychologist_id)
        print(f"   • Resultados ML retornados: {len(ml_risk_analysis)}")

        if not ml_risk_analysis:
            ml_risk_analysis = []

        # Filtra pacientes de alto e moderado risco
        high_risk_patients = [p for p in ml_risk_analysis if p.get("risk", "").lower() in ["alto", "moderado"]]

        # Cria estatísticas para o relatório
        stats = ReportStats(
            active_patients=len(patients),
            total_sessions=total_sessions,
            completed_sessions=completed_sessions,
            canceled_sessions=canceled_sessions,
            scheduled_sessions=scheduled_sessions,
            attendance_rate=f"{attendance_rate:.1f}",
            risk_alerts=high_risk_patients
        )

        print("✅ [REPORT] Estatísticas geradas com sucesso")

        # Retorna relatório completo
        return ReportsData(
            stats=stats,
            risk_alerts=high_risk_patients
        )

    except Exception as e:
        import traceback
        print("❌ [REPORT] ERRO AO GERAR RELATÓRIO")
        traceback.print_exc()
        raise e
