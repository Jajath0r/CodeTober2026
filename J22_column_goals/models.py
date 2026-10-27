from enum import StrEnum

class StatusType(StrEnum):
    COMPLETED = "completed"
    PENDING = "pending"
    CANCELLED = "cancelled"
    