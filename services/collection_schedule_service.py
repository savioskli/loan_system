from models.collection_schedule import CollectionSchedule
from extensions import db

class CollectionScheduleService:

    @staticmethod
    def create_schedule(data):
        new_schedule = CollectionSchedule(
            staff_id=data['staff_id'],
            loan_id=data['loan_id'],
            schedule_date=datetime.strptime(data['schedule_date'], '%Y-%m-%dT%H:%M:%S'),
            status=data['status']
        )
        db.session.add(new_schedule)
        db.session.commit()
        return new_schedule

    @staticmethod
    def get_schedules(filters=None):
        query = CollectionSchedule.query
        if filters:
            if 'staff_id' in filters:
                query = query.filter_by(staff_id=filters['staff_id'])
            if 'loan_status' in filters:
                query = query.join(Loan).filter(Loan.status == filters['loan_status'])
        return query.all()

    @staticmethod
    def update_schedule(schedule_id, data):
        schedule = CollectionSchedule.query.get_or_404(schedule_id)
        schedule.staff_id = data.get('staff_id', schedule.staff_id)
        schedule.loan_id = data.get('loan_id', schedule.loan_id)
        schedule.schedule_date = datetime.strptime(data['schedule_date'], '%Y-%m-%dT%H:%M:%S')
        schedule.status = data.get('status', schedule.status)
        db.session.commit()
        return schedule

    @staticmethod
    def delete_schedule(schedule_id):
        schedule = CollectionSchedule.query.get_or_404(schedule_id)
        db.session.delete(schedule)
        db.session.commit()
