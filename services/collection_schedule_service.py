from models.collection_schedule import CollectionSchedule
from models.loan import Loan
from models.staff import Staff
from extensions import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from flask import current_app
import traceback
import requests

# Mock client data from core banking
CORE_BANKING_URL = "http://localhost:5003"

class CollectionScheduleService:
    @staticmethod
    def get_client_name(client_id):
        """Get client name from core banking system."""
        try:
            response = requests.get(f"{CORE_BANKING_URL}/api/clients/search", params={'client_id': client_id})
            if response.status_code == 200:
                clients = response.json()
                if clients:
                    return clients[0].get('name')
            return None
        except Exception as e:
            current_app.logger.error(f"Error fetching client from core banking: {str(e)}")
            return None

    @staticmethod
    def create_schedule(data):
        """Create a new collection schedule."""
        try:
            current_app.logger.info("Creating new collection schedule")
            current_app.logger.debug(f"Schedule data: {data}")
            
            new_schedule = CollectionSchedule(
                # Staff Assignment
                staff_id=data.get('staff_id'),
                loan_id=data.get('loan_id'),
                supervisor_id=data.get('supervisor_id'),
                assigned_branch=data.get('assigned_branch'),
                assignment_date=datetime.strptime(data.get('assignment_date'), '%Y-%m-%dT%H:%M') if data.get('assignment_date') else datetime.utcnow(),
                follow_up_deadline=datetime.strptime(data.get('follow_up_deadline'), '%Y-%m-%dT%H:%M'),
                collection_priority=data.get('collection_priority', 'Medium'),
                
                # Follow-up Plan
                follow_up_frequency=data.get('follow_up_frequency'),
                next_follow_up_date=datetime.strptime(data.get('next_follow_up_date'), '%Y-%m-%dT%H:%M'),
                preferred_collection_method=data.get('preferred_collection_method'),
                promised_payment_date=datetime.strptime(data.get('promised_payment_date'), '%Y-%m-%dT%H:%M') if data.get('promised_payment_date') else None,
                attempts_allowed=data.get('attempts_allowed', 3),
                attempts_made=0,
                
                # Task Details
                task_description=data.get('task_description'),
                progress_status='Not Started',
                escalation_level=data.get('escalation_level'),
                
                # Initial Review
                special_instructions=data.get('special_instructions')
            )
            
            db.session.add(new_schedule)
            db.session.commit()
            current_app.logger.info(f"Created schedule with ID: {new_schedule.id}")
            return new_schedule
            
        except Exception as e:
            current_app.logger.error(f"Error creating schedule: {str(e)}\n{traceback.format_exc()}")
            db.session.rollback()
            raise

    @staticmethod
    def get_schedules(filters=None):
        """Get collection schedules with optional filters."""
        try:
            current_app.logger.info("Starting get_schedules service method")
            current_app.logger.debug(f"Filters: {filters}")
            
            # Start with a base query, selecting only needed columns
            query = db.session.query(
                CollectionSchedule,
                Staff.first_name.label('staff_first_name'),
                Staff.last_name.label('staff_last_name'),
                Loan.account_no.label('loan_account'),
                Loan.client_id.label('client_id')
            ).outerjoin(
                Staff, Staff.id == CollectionSchedule.staff_id
            ).outerjoin(
                Loan, Loan.id == CollectionSchedule.loan_id
            )
            
            if filters:
                current_app.logger.info(f"Applying filters: {filters}")
                if filters.get('staff_id'):
                    query = query.filter(CollectionSchedule.staff_id == filters['staff_id'])
                if filters.get('loan_id'):
                    query = query.filter(CollectionSchedule.loan_id == filters['loan_id'])
                if filters.get('priority'):
                    query = query.filter(CollectionSchedule.collection_priority == filters['priority'])
                if filters.get('status'):
                    query = query.filter(CollectionSchedule.progress_status == filters['status'])
                if filters.get('date_from'):
                    query = query.filter(CollectionSchedule.next_follow_up_date >= filters['date_from'])
                if filters.get('date_to'):
                    query = query.filter(CollectionSchedule.next_follow_up_date <= filters['date_to'])
                if filters.get('escalation_level'):
                    query = query.filter(CollectionSchedule.escalation_level == filters['escalation_level'])

            current_app.logger.info("Executing query...")
            results = query.order_by(CollectionSchedule.next_follow_up_date.asc()).all()
            current_app.logger.info(f"Found {len(results)} schedules")
            
            schedules_list = []
            for schedule, staff_first_name, staff_last_name, loan_account, client_id in results:
                try:
                    # Construct staff name
                    staff_name = f"{staff_first_name} {staff_last_name}" if staff_first_name and staff_last_name else None
                    
                    # Get client name from core banking
                    client_name = CollectionScheduleService.get_client_name(client_id) if client_id else None
                    
                    schedule_dict = {
                        'id': schedule.id,
                        'staff_id': schedule.staff_id,
                        'staff_name': staff_name,
                        'loan_id': schedule.loan_id,
                        'loan_account': loan_account,
                        'borrower_name': client_name,
                        'assigned_branch': schedule.assigned_branch,
                        'collection_priority': schedule.collection_priority,
                        'follow_up_frequency': schedule.follow_up_frequency,
                        'next_follow_up_date': schedule.next_follow_up_date.isoformat() if schedule.next_follow_up_date else None,
                        'preferred_collection_method': schedule.preferred_collection_method,
                        'promised_payment_date': schedule.promised_payment_date.isoformat() if schedule.promised_payment_date else None,
                        'attempts_made': schedule.attempts_made,
                        'attempts_allowed': schedule.attempts_allowed,
                        'progress_status': schedule.progress_status,
                        'escalation_level': schedule.escalation_level,
                        'task_description': schedule.task_description,
                        'special_instructions': schedule.special_instructions
                    }
                    current_app.logger.debug(f"Schedule {schedule.id} data: {schedule_dict}")
                    schedules_list.append(schedule_dict)
                    
                except Exception as e:
                    current_app.logger.error(f"Error processing schedule {schedule.id}: {str(e)}\n{traceback.format_exc()}")
                    continue
            
            return schedules_list
        except Exception as e:
            current_app.logger.error(f"Error in get_schedules: {str(e)}\n{traceback.format_exc()}")
            raise

    @staticmethod
    def get_schedule(schedule_id):
        """Get a specific collection schedule."""
        try:
            current_app.logger.info(f"Getting schedule with ID: {schedule_id}")
            return CollectionSchedule.query.get_or_404(schedule_id)
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in get_schedule: {str(e)}")
            raise
        except Exception as e:
            current_app.logger.error(f"Error in get_schedule: {str(e)}")
            raise

    @staticmethod
    def update_schedule(schedule_id, data):
        """Update an existing collection schedule."""
        try:
            current_app.logger.info(f"Updating schedule with ID: {schedule_id}")
            current_app.logger.debug(f"Update data: {data}")
            
            schedule = CollectionSchedule.query.get_or_404(schedule_id)
            
            # Update Staff Assignment
            if 'staff_id' in data:
                schedule.staff_id = data['staff_id']
            if 'supervisor_id' in data:
                schedule.supervisor_id = data['supervisor_id']
            if 'assigned_branch' in data:
                schedule.assigned_branch = data['assigned_branch']
            if 'follow_up_deadline' in data:
                schedule.follow_up_deadline = datetime.strptime(data['follow_up_deadline'], '%Y-%m-%dT%H:%M')
            if 'collection_priority' in data:
                schedule.collection_priority = data['collection_priority']
            
            # Update Follow-up Plan
            if 'follow_up_frequency' in data:
                schedule.follow_up_frequency = data['follow_up_frequency']
            if 'next_follow_up_date' in data:
                schedule.next_follow_up_date = datetime.strptime(data['next_follow_up_date'], '%Y-%m-%dT%H:%M')
            if 'preferred_collection_method' in data:
                schedule.preferred_collection_method = data['preferred_collection_method']
            if 'promised_payment_date' in data:
                schedule.promised_payment_date = datetime.strptime(data['promised_payment_date'], '%Y-%m-%dT%H:%M') if data['promised_payment_date'] else None
            if 'attempts_allowed' in data:
                schedule.attempts_allowed = data['attempts_allowed']
            
            # Update Task & Progress
            if 'task_description' in data:
                schedule.task_description = data['task_description']
            if 'progress_status' in data:
                schedule.progress_status = data['progress_status']
            if 'escalation_level' in data:
                schedule.escalation_level = data['escalation_level']
            if 'resolution_date' in data:
                schedule.resolution_date = datetime.strptime(data['resolution_date'], '%Y-%m-%dT%H:%M') if data['resolution_date'] else None
            
            # Update Review Information
            if 'reviewed_by' in data:
                schedule.reviewed_by = data['reviewed_by']
                schedule.approval_date = datetime.utcnow()
            if 'special_instructions' in data:
                schedule.special_instructions = data['special_instructions']
            
            # Increment attempts if specified
            if data.get('increment_attempts', False):
                schedule.attempts_made += 1
            
            db.session.commit()
            current_app.logger.info(f"Updated schedule with ID: {schedule_id}")
            return schedule
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in update_schedule: {str(e)}")
            db.session.rollback()
            raise
        except Exception as e:
            current_app.logger.error(f"Error in update_schedule: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def delete_schedule(schedule_id):
        """Delete a collection schedule."""
        try:
            current_app.logger.info(f"Deleting schedule with ID: {schedule_id}")
            schedule = CollectionSchedule.query.get_or_404(schedule_id)
            db.session.delete(schedule)
            db.session.commit()
            current_app.logger.info(f"Deleted schedule with ID: {schedule_id}")
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in delete_schedule: {str(e)}")
            db.session.rollback()
            raise
        except Exception as e:
            current_app.logger.error(f"Error in delete_schedule: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def update_progress(schedule_id, new_status, resolution_date=None):
        """Update the progress status of a schedule."""
        try:
            current_app.logger.info(f"Updating progress of schedule with ID: {schedule_id}")
            current_app.logger.debug(f"New status: {new_status}, Resolution date: {resolution_date}")
            
            schedule = CollectionSchedule.query.get_or_404(schedule_id)
            schedule.progress_status = new_status
            if new_status == 'Completed' and resolution_date:
                schedule.resolution_date = resolution_date
            db.session.commit()
            current_app.logger.info(f"Updated progress of schedule with ID: {schedule_id}")
            return schedule
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in update_progress: {str(e)}")
            db.session.rollback()
            raise
        except Exception as e:
            current_app.logger.error(f"Error in update_progress: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def escalate_schedule(schedule_id, escalation_level, notes=None):
        """Escalate a collection schedule."""
        try:
            current_app.logger.info(f"Escalating schedule with ID: {schedule_id}")
            current_app.logger.debug(f"Escalation level: {escalation_level}, Notes: {notes}")
            
            schedule = CollectionSchedule.query.get_or_404(schedule_id)
            schedule.escalation_level = escalation_level
            schedule.progress_status = 'Escalated'
            if notes:
                schedule.special_instructions = (schedule.special_instructions or '') + f"\n[Escalation Notes]: {notes}"
            db.session.commit()
            current_app.logger.info(f"Escalated schedule with ID: {schedule_id}")
            return schedule
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in escalate_schedule: {str(e)}")
            db.session.rollback()
            raise
        except Exception as e:
            current_app.logger.error(f"Error in escalate_schedule: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def approve_schedule(schedule_id, reviewer_id, instructions=None):
        """Approve a collection schedule."""
        try:
            current_app.logger.info(f"Approving schedule with ID: {schedule_id}")
            current_app.logger.debug(f"Reviewer ID: {reviewer_id}, Instructions: {instructions}")
            
            schedule = CollectionSchedule.query.get_or_404(schedule_id)
            schedule.reviewed_by = reviewer_id
            schedule.approval_date = datetime.utcnow()
            if instructions:
                schedule.special_instructions = instructions
            db.session.commit()
            current_app.logger.info(f"Approved schedule with ID: {schedule_id}")
            return schedule
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in approve_schedule: {str(e)}")
            db.session.rollback()
            raise
        except Exception as e:
            current_app.logger.error(f"Error in approve_schedule: {str(e)}")
            db.session.rollback()
            raise