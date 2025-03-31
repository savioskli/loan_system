from models.collection_schedule import CollectionSchedule
from models.loan import Loan
from models.staff import Staff
from models.branch import Branch
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
            current_app.logger.info(f"Fetching client name for ID: {client_id}")
            if not client_id:
                current_app.logger.warning("No client_id provided")
                return None

            response = requests.get(f"{CORE_BANKING_URL}/api/clients/search", params={'client_id': client_id})
            current_app.logger.info(f"Core banking API response status: {response.status_code}")
            
            if response.status_code == 200:
                clients = response.json()
                current_app.logger.info(f"Core banking API response data: {clients}")
                if clients:
                    client_name = clients[0].get('name')
                    current_app.logger.info(f"Found client name: {client_name}")
                    return client_name
                else:
                    current_app.logger.warning("No clients found in response")
            else:
                current_app.logger.error(f"Core banking API error: {response.text}")
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
                staff_id=data.get('assigned_id'),  # Changed from staff_id to assigned_id
                loan_id=data.get('loan_id'),
                supervisor_id=data.get('supervisor_id'),
                manager_id=data.get('manager_id'),
                assigned_branch=data.get('branch_id'),  # Changed from assigned_branch to branch_id
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
                
                # Loan Details
                outstanding_balance=float(data.get('outstanding_balance', 0)),
                missed_payments=int(data.get('missed_payments', 0)),
                
                # Contact Details
                best_contact_time=data.get('best_contact_time'),
                collection_location=data.get('collection_location'),
                alternative_contact=data.get('alternative_contact'),
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
        """Get collection schedules with optional filters and pagination."""
        try:
            current_app.logger.info("Starting get_schedules service method")
            current_app.logger.debug(f"Filters: {filters}")
            
            # Start with a base query, selecting only needed columns
            query = db.session.query(
                CollectionSchedule,
                Staff.first_name.label('staff_first_name'),
                Staff.last_name.label('staff_last_name'),
                Loan.account_no.label('loan_account'),
                Loan.client_id.label('client_id'),
                Branch.name.label('branch_name')
            ).outerjoin(
                Staff, Staff.id == CollectionSchedule.assigned_id
            ).outerjoin(
                Loan, Loan.id == CollectionSchedule.loan_id
            ).outerjoin(
                Branch, Branch.id == db.cast(CollectionSchedule.assigned_branch, db.Integer)
            )
            
            if filters:
                current_app.logger.info(f"Applying filters: {filters}")
                if filters.get('assigned_id'):
                    query = query.filter(CollectionSchedule.assigned_id == filters['assigned_id'])
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

            # Get total count before pagination
            total_count = query.count()
            
            # Apply pagination if specified in filters
            page = int(filters.get('page', 1))
            per_page = int(filters.get('per_page', 10))
            offset = (page - 1) * per_page
            
            current_app.logger.info("Executing paginated query...")
            results = query.order_by(CollectionSchedule.next_follow_up_date.asc())\
                          .offset(offset)\
                          .limit(per_page)\
                          .all()
            current_app.logger.info(f"Found {len(results)} schedules for page {page}")
            
            schedules_list = []
            for result in results:
                schedule = result[0]
                staff_first_name = result.staff_first_name
                staff_last_name = result.staff_last_name
                loan_account = result.loan_account
                client_id = result.client_id
                branch_name = result.branch_name
                try:
                    # Construct staff name
                    staff_name = f"{staff_first_name} {staff_last_name}" if staff_first_name and staff_last_name else None
                    
                    # Get client name from core banking
                    client_name = CollectionScheduleService.get_client_name(client_id) if client_id else None
                    
                    # Get supervisor name if available
                    supervisor_name = None
                    if schedule.supervisor_id:
                        supervisor = Staff.query.get(schedule.supervisor_id)
                        if supervisor:
                            supervisor_name = f"{supervisor.first_name} {supervisor.last_name}"
                    
                    schedule_dict = {
                        'id': schedule.id,
                        'assigned_id': schedule.assigned_id,
                        'staff_name': staff_name,
                        'loan_id': schedule.loan_id,
                        'loan_account': loan_account,
                        'borrower_name': client_name,
                        'supervisor_id': schedule.supervisor_id,
                        'supervisor_name': supervisor_name,
                        'assigned_branch': schedule.assigned_branch,
                        'branch_name': branch_name,
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
                        'special_instructions': schedule.special_instructions,
                        'outstanding_balance': schedule.outstanding_balance,
                        'missed_payments': schedule.missed_payments,
                        'best_contact_time': schedule.best_contact_time,
                        'alternative_contact': schedule.alternative_contact
                    }
                    current_app.logger.debug(f"Schedule {schedule.id} data: {schedule_dict}")
                    schedules_list.append(schedule_dict)
                    
                except Exception as e:
                    current_app.logger.error(f"Error processing schedule {schedule.id}: {str(e)}\n{traceback.format_exc()}")
                    continue
            
            # Return with pagination info
            return {
                'items': schedules_list,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_count,
                    'pages': (total_count + per_page - 1) // per_page
                }
            }
        except Exception as e:
            current_app.logger.error(f"Error in get_schedules: {str(e)}\n{traceback.format_exc()}")
            raise

    @staticmethod
    def get_schedule(schedule_id):
        """Get a specific collection schedule."""
        try:
            current_app.logger.info(f"Getting schedule with ID: {schedule_id}")
            schedule = CollectionSchedule.query.get_or_404(schedule_id)
            
            # Get staff name
            staff_name = f"{schedule.staff.first_name} {schedule.staff.last_name}" if schedule.staff else None
            
            # Get supervisor name
            supervisor_name = f"{schedule.supervisor.first_name} {schedule.supervisor.last_name}" if schedule.supervisor else None
            
            # Get manager name
            manager_name = f"{schedule.manager.first_name} {schedule.manager.last_name}" if schedule.manager else None
            
            # Get loan details
            loan_account = schedule.loan.account_no if schedule.loan else None
            borrower_name = schedule.loan.client.full_name if schedule.loan and schedule.loan.client else None
            client_id = schedule.loan.client.id if schedule.loan and schedule.loan.client else None
            
            return {
                'id': schedule.id,
                'assigned_id': schedule.assigned_id,
                'staff_name': staff_name,
                'supervisor_id': schedule.supervisor_id,
                'supervisor_name': supervisor_name,
                'manager_id': schedule.manager_id,
                'manager_name': manager_name,
                'loan_id': schedule.loan_id,
                'loan_account': loan_account,
                'borrower_name': borrower_name,
                'client_id': client_id,
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
                'special_instructions': schedule.special_instructions,
                'outstanding_balance': schedule.outstanding_balance,
                'missed_payments': schedule.missed_payments,
                'best_contact_time': schedule.best_contact_time,
                'alternative_contact': schedule.alternative_contact,
                'collection_location': schedule.collection_location
            }
            
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in get_schedule: {str(e)}")
            raise
        except Exception as e:
            current_app.logger.error(f"Error in get_schedule: {str(e)}")
            raise

    @staticmethod
    def get_schedule_by_id(schedule_id):
        """Get a collection schedule by ID without raising 404."""
        try:
            current_app.logger.info(f"Getting schedule with ID: {schedule_id}")
            return CollectionSchedule.query.get(schedule_id)
        except Exception as e:
            current_app.logger.error(f"Error in get_schedule_by_id: {str(e)}")
            return None

    @staticmethod
    def update_schedule(schedule_id, data):
        """Update an existing collection schedule."""
        try:
            current_app.logger.info(f"Updating schedule with ID: {schedule_id}")
            current_app.logger.debug(f"Update data: {data}")
            
            schedule = CollectionSchedule.query.get_or_404(schedule_id)
            
            # Update Staff Assignment
            if 'assigned_id' in data:
                schedule.assigned_id = data['assigned_id']
            if 'supervisor_id' in data:
                schedule.supervisor_id = data['supervisor_id']
            if 'manager_id' in data:
                schedule.manager_id = data['manager_id']
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
                schedule.promised_payment_date = datetime.strptime(data['promised_payment_date'], '%Y-%m-%dT%H:%M') if data.get('promised_payment_date') else None
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