from app import application
from extensions import db
from models import Compound, TitrationTemplate

with application.app_context():
    db.create_all()

    compounds = [
        dict(name="Semaglutide",   category="GLP-1",        default_route="SubQ",       typical_dose_min=0.25,  typical_dose_max=2.4,   dose_unit="mg", frequency="Weekly",    has_titration=True,  titration_notes="Start 0.25mg/wk x4, then 0.5mg x4, then 1mg x4, then 1.7mg, then 2.4mg"),
        dict(name="Tirzepatide",   category="GLP-1",        default_route="SubQ",       typical_dose_min=2.5,   typical_dose_max=15.0,  dose_unit="mg", frequency="Weekly",    has_titration=True,  titration_notes="Start 2.5mg/wk x4, then 5mg x4, then 7.5mg x4, then 10mg x4, then 12.5mg x4, then 15mg"),
        dict(name="Retatrutide",   category="GLP-1",        default_route="SubQ",       typical_dose_min=0.5,   typical_dose_max=12.0,  dose_unit="mg", frequency="Weekly",    has_titration=True,  titration_notes="Start 0.5mg/wk x4, then 2mg x4, then 4mg x4, then 8mg x4, then 12mg"),
        dict(name="Tesamorelin",   category="GH/Body Comp", default_route="SubQ",       typical_dose_min=1.0,   typical_dose_max=2.0,   dose_unit="mg", frequency="Daily",     has_titration=False, notes="Inject fasted AM. Stimulates pulsatile GH release. Track IGF-1."),
        dict(name="GLOW",          category="GH/Body Comp", default_route="SubQ",       typical_dose_min=0.1,   typical_dose_max=0.3,   dose_unit="mg", frequency="Daily",     has_titration=False, notes="GH releasing blend. Inject pre-bed fasted."),
        dict(name="KLOW",          category="GH/Body Comp", default_route="SubQ",       typical_dose_min=0.1,   typical_dose_max=0.3,   dose_unit="mg", frequency="Daily",     has_titration=False, notes="GH/body comp blend. Inject pre-bed fasted."),
        dict(name="PT-141",        category="Sexual Health",default_route="SubQ",       typical_dose_min=0.5,   typical_dose_max=2.0,   dose_unit="mg", frequency="As needed", has_titration=False, notes="Bremelanotide. Use 45-60 min before activity."),
        dict(name="Kisspeptin",    category="Sexual Health",default_route="SubQ",       typical_dose_min=0.01,  typical_dose_max=0.1,   dose_unit="mg", frequency="As needed", has_titration=False, notes="Pulsatile dosing. Track LH/FSH/testosterone response."),
        dict(name="Semax",         category="Cognitive",    default_route="Intranasal", typical_dose_min=0.1,   typical_dose_max=0.6,   dose_unit="mg", frequency="Daily",     has_titration=False, notes="Cycle 2 weeks on, 2 weeks off."),
        dict(name="Selank",        category="Cognitive",    default_route="Intranasal", typical_dose_min=0.1,   typical_dose_max=0.3,   dose_unit="mg", frequency="Daily",     has_titration=False, notes="Anxiolytic. Can stack with Semax."),
        dict(name="NAD+",          category="Energy",       default_route="SubQ",       typical_dose_min=100.0, typical_dose_max=500.0, dose_unit="mg", frequency="Daily",     has_titration=False, notes="Start low (100mg). IV push slowly to avoid flushing."),
    ]

    added = 0
    for c_data in compounds:
        if not Compound.query.filter_by(name=c_data["name"]).first():
            db.session.add(Compound(**c_data))
            added += 1
    db.session.commit()
    print(f"Compounds added: {added}")

    titration_data = {
        "Semaglutide": [(1,0.25),(2,0.25),(3,0.25),(4,0.25),(5,0.5),(6,0.5),(7,0.5),(8,0.5),(9,1.0),(10,1.0),(11,1.0),(12,1.0),(13,1.7),(14,1.7),(15,1.7),(16,1.7),(17,2.4)],
        "Tirzepatide": [(1,2.5),(2,2.5),(3,2.5),(4,2.5),(5,5.0),(6,5.0),(7,5.0),(8,5.0),(9,7.5),(10,7.5),(11,7.5),(12,7.5),(13,10.0),(14,10.0),(15,10.0),(16,10.0),(17,12.5),(18,12.5),(19,12.5),(20,12.5),(21,15.0)],
        "Retatrutide": [(1,0.5),(2,0.5),(3,0.5),(4,0.5),(5,2.0),(6,2.0),(7,2.0),(8,2.0),(9,4.0),(10,4.0),(11,4.0),(12,4.0),(13,8.0),(14,8.0),(15,8.0),(16,8.0),(17,12.0)],
    }

    t_added = 0
    for compound_name, steps in titration_data.items():
        compound = Compound.query.filter_by(name=compound_name).first()
        if not compound:
            continue
        if TitrationTemplate.query.filter_by(compound_id=compound.id).count() == 0:
            for week, dose in steps:
                db.session.add(TitrationTemplate(compound_id=compound.id, week_number=week, dose_mg=dose))
                t_added += 1
    db.session.commit()
    print(f"Titration steps added: {t_added}")
    print("Done!")
