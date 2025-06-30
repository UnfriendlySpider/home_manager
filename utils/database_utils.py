"""
Database utility functions
Helper functions for common database operations
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

def paginate_query(query, page: int = 1, per_page: int = 25):
    """Paginate a SQLAlchemy query"""
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
        "has_prev": page > 1,
        "has_next": page * per_page < total
    }

def search_filter(query, model, search_term: str, search_fields: List[str]):
    """Add search filter to query"""
    if not search_term:
        return query
    
    search_conditions = []
    for field in search_fields:
        if hasattr(model, field):
            attr = getattr(model, field)
            search_conditions.append(attr.like(f"%{search_term}%"))
    
    if search_conditions:
        query = query.filter(or_(*search_conditions))
    
    return query

def date_range_filter(query, model, field_name: str, start_date: date = None, end_date: date = None):
    """Add date range filter to query"""
    if not hasattr(model, field_name):
        return query
    
    field = getattr(model, field_name)
    
    if start_date:
        query = query.filter(field >= start_date)
    if end_date:
        query = query.filter(field <= end_date)
    
    return query

def sort_query(query, model, sort_field: str = None, sort_direction: str = "asc"):
    """Add sorting to query"""
    if not sort_field or not hasattr(model, sort_field):
        return query
    
    field = getattr(model, sort_field)
    
    if sort_direction.lower() == "desc":
        return query.order_by(desc(field))
    else:
        return query.order_by(asc(field))

def bulk_insert(db: Session, model_class, data_list: List[Dict[str, Any]]):
    """Bulk insert records"""
    try:
        objects = [model_class(**data) for data in data_list]
        db.bulk_save_objects(objects)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Bulk insert error: {e}")
        return False

def bulk_update(db: Session, model_class, updates: List[Dict[str, Any]], id_field: str = "id"):
    """Bulk update records"""
    try:
        for update_data in updates:
            record_id = update_data.pop(id_field)
            db.query(model_class).filter(
                getattr(model_class, id_field) == record_id
            ).update(update_data)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Bulk update error: {e}")
        return False

def soft_delete_record(db: Session, model_instance):
    """Soft delete a record (if model supports it)"""
    if hasattr(model_instance, 'soft_delete'):
        model_instance.soft_delete()
        db.commit()
        return True
    return False

def restore_record(db: Session, model_instance):
    """Restore a soft-deleted record"""
    if hasattr(model_instance, 'restore'):
        model_instance.restore()
        db.commit()
        return True
    return False

def get_or_create(db: Session, model_class, defaults: Dict = None, **kwargs):
    """Get existing record or create new one"""
    instance = db.query(model_class).filter_by(**kwargs).first()
    
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.items())
        if defaults:
            params.update(defaults)
        instance = model_class(**params)
        db.add(instance)
        db.commit()
        return instance, True

def count_by_field(db: Session, model_class, field_name: str):
    """Count records grouped by field value"""
    from sqlalchemy import func
    
    if not hasattr(model_class, field_name):
        return {}
    
    field = getattr(model_class, field_name)
    results = db.query(field, func.count(field)).group_by(field).all()
    
    return {str(value): count for value, count in results}

def get_recent_records(db: Session, model_class, days: int = 7, date_field: str = "created_at"):
    """Get records created in the last N days"""
    if not hasattr(model_class, date_field):
        return []
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    field = getattr(model_class, date_field)
    
    return db.query(model_class).filter(field >= cutoff_date).all()

def calculate_aggregates(db: Session, model_class, field_name: str, filters: Dict = None):
    """Calculate sum, avg, min, max for a numeric field"""
    from sqlalchemy import func
    
    if not hasattr(model_class, field_name):
        return {}
    
    query = db.query(model_class)
    
    # Apply filters if provided
    if filters:
        for field, value in filters.items():
            if hasattr(model_class, field):
                query = query.filter(getattr(model_class, field) == value)
    
    field = getattr(model_class, field_name)
    
    result = query.with_entities(
        func.sum(field).label('total'),
        func.avg(field).label('average'),
        func.min(field).label('minimum'),
        func.max(field).label('maximum'),
        func.count(field).label('count')
    ).first()
    
    return {
        'sum': float(result.total or 0),
        'avg': float(result.average or 0),
        'min': float(result.minimum or 0),
        'max': float(result.maximum or 0),
        'count': int(result.count or 0)
    }

def export_to_dict(records, exclude_fields: List[str] = None):
    """Export database records to list of dictionaries"""
    if exclude_fields is None:
        exclude_fields = []
    
    result = []
    for record in records:
        record_dict = record.to_dict() if hasattr(record, 'to_dict') else {}
        
        # Remove excluded fields
        for field in exclude_fields:
            record_dict.pop(field, None)
        
        result.append(record_dict)
    
    return result

def import_from_dict(db: Session, model_class, data_list: List[Dict], update_existing: bool = False):
    """Import data from list of dictionaries"""
    created_count = 0
    updated_count = 0
    error_count = 0
    
    for data in data_list:
        try:
            # Check if record exists (assuming 'id' field)
            record_id = data.get('id')
            existing_record = None
            
            if record_id:
                existing_record = db.query(model_class).filter(
                    model_class.id == record_id
                ).first()
            
            if existing_record and update_existing:
                # Update existing record
                existing_record.update_from_dict(data)
                updated_count += 1
            elif not existing_record:
                # Create new record
                new_record = model_class(**data)
                db.add(new_record)
                created_count += 1
            
        except Exception as e:
            print(f"Import error for record {data}: {e}")
            error_count += 1
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Import commit error: {e}")
        return {"error": str(e)}
    
    return {
        "created": created_count,
        "updated": updated_count,
        "errors": error_count
    }
