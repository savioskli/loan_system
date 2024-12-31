"""
Database manager for core banking system
"""
from extensions import db
from models.core_banking import CoreBankingSystem, CoreBankingEndpoint, CoreBankingLog
from datetime import datetime

class DatabaseManager:
    @staticmethod
    def init_db():
        """Initialize database tables"""
        db.create_all()

    @staticmethod
    def drop_db():
        """Drop all database tables"""
        db.drop_all()

    @staticmethod
    def reset_db():
        """Reset database (drop and recreate tables)"""
        DatabaseManager.drop_db()
        DatabaseManager.init_db()

    @staticmethod
    def get_all_systems():
        """Get all banking systems"""
        return CoreBankingSystem.query.all()

    @staticmethod
    def get_active_systems():
        """Get all active banking systems"""
        return CoreBankingSystem.query.filter_by(is_active=True).all()

    @staticmethod
    def get_system_by_id(system_id):
        """Get banking system by ID"""
        return CoreBankingSystem.query.get(system_id)

    @staticmethod
    def get_system_by_name(name):
        """Get banking system by name"""
        return CoreBankingSystem.query.filter_by(name=name).first()

    @staticmethod
    def get_system_endpoints(system_id):
        """Get all endpoints for a banking system"""
        return CoreBankingEndpoint.query.filter_by(system_id=system_id).all()

    @staticmethod
    def get_active_endpoints(system_id):
        """Get active endpoints for a banking system"""
        return CoreBankingEndpoint.query.filter_by(
            system_id=system_id,
            is_active=True
        ).all()

    @staticmethod
    def get_endpoint_by_id(endpoint_id):
        """Get endpoint by ID"""
        return CoreBankingEndpoint.query.get(endpoint_id)

    @staticmethod
    def get_endpoint_by_name(system_id, name):
        """Get endpoint by name within a system"""
        return CoreBankingEndpoint.query.filter_by(
            system_id=system_id,
            name=name
        ).first()

    @staticmethod
    def get_logs(system_id=None, endpoint_id=None, start_date=None, end_date=None):
        """Get API request logs with optional filters"""
        query = CoreBankingLog.query

        if system_id:
            query = query.filter_by(system_id=system_id)
        if endpoint_id:
            query = query.filter_by(endpoint_id=endpoint_id)
        if start_date:
            query = query.filter(CoreBankingLog.created_at >= start_date)
        if end_date:
            query = query.filter(CoreBankingLog.created_at <= end_date)

        return query.order_by(CoreBankingLog.created_at.desc()).all()

    @staticmethod
    def get_error_logs(system_id=None, endpoint_id=None, start_date=None, end_date=None):
        """Get error logs with optional filters"""
        query = CoreBankingLog.query.filter(CoreBankingLog.error_message.isnot(None))

        if system_id:
            query = query.filter_by(system_id=system_id)
        if endpoint_id:
            query = query.filter_by(endpoint_id=endpoint_id)
        if start_date:
            query = query.filter(CoreBankingLog.created_at >= start_date)
        if end_date:
            query = query.filter(CoreBankingLog.created_at <= end_date)

        return query.order_by(CoreBankingLog.created_at.desc()).all()

    @staticmethod
    def delete_old_logs(days=30):
        """Delete logs older than specified days"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            CoreBankingLog.query.filter(CoreBankingLog.created_at < cutoff_date).delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete old logs: {str(e)}")

    @staticmethod
    def get_system_stats(system_id):
        """Get statistics for a banking system"""
        try:
            total_requests = CoreBankingLog.query.filter_by(system_id=system_id).count()
            error_requests = CoreBankingLog.query.filter_by(system_id=system_id).filter(
                CoreBankingLog.error_message.isnot(None)
            ).count()
            active_endpoints = CoreBankingEndpoint.query.filter_by(
                system_id=system_id,
                is_active=True
            ).count()

            return {
                'total_requests': total_requests,
                'error_requests': error_requests,
                'success_rate': ((total_requests - error_requests) / total_requests * 100) if total_requests > 0 else 0,
                'active_endpoints': active_endpoints
            }
        except Exception as e:
            raise Exception(f"Failed to get system stats: {str(e)}")

    @staticmethod
    def get_endpoint_stats(endpoint_id):
        """Get statistics for an endpoint"""
        try:
            total_requests = CoreBankingLog.query.filter_by(endpoint_id=endpoint_id).count()
            error_requests = CoreBankingLog.query.filter_by(endpoint_id=endpoint_id).filter(
                CoreBankingLog.error_message.isnot(None)
            ).count()

            return {
                'total_requests': total_requests,
                'error_requests': error_requests,
                'success_rate': ((total_requests - error_requests) / total_requests * 100) if total_requests > 0 else 0
            }
        except Exception as e:
            raise Exception(f"Failed to get endpoint stats: {str(e)}")
