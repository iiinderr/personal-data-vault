
from services.audit import AuditLogger, AuditAction

logger = AuditLogger()

logger.log(
    action=AuditAction.LOGIN_SUCCESS,
    user_id=1,
    details="User logged in"
)

logs = logger.get_logs_for_user(1)

for log in logs:
    print(log.action)

