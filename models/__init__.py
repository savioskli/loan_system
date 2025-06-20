from extensions import db

from .client_type import ClientType
from .staff import Staff
from .system_settings import SystemSettings
from .activity_log import ActivityLog
from .branch import Branch
from .sms_template import SMSTemplate
from .loan import Loan
from .client import Client
from .product import Product
from .calendar_event import CalendarEvent
from .guarantor import Guarantor
from .collection_schedule import CollectionSchedule, CollectionScheduleProgress
from .workflow import Workflow, CollectionWorkflowStep
from .prospect_registration import ProspectRegistration
from .corporate_official import CorporateOfficial
from .corporate_signatory import CorporateSignatory
from .corporate_attachment import CorporateAttachment
from .corporate_service import CorporateService

__all__ = [
    'db',
    'ClientType', 
    'Staff', 
    'SystemSettings', 
    'ActivityLog', 
    'Branch', 
    'SMSTemplate', 
    'Loan', 
    'Client', 
    'Product',
    'CalendarEvent',
    'Guarantor',
    'CollectionSchedule',
    'CollectionScheduleProgress',
    'Workflow',
    'CollectionWorkflowStep',
    'ProspectRegistration',
    'CorporateOfficial',
    'CorporateSignatory',
    'CorporateAttachment',
    'CorporateService'
]
