# --- USER SERVICE ---
from app.services.user import (
    create_user,
    get_users,
    get_user_by_id,
    get_user_by_email,
    update_user_by_id,
    delete_user,
    authenticate_user,
    change_user_password,
)

# --- APPLICATION SERVICE ---
from app.services.application import (
    create_application,
    get_applications,
    get_applications_by_user,
    get_application_by_id,
    get_application_by_key,
    update_application_by_id,
    delete_application,
    authenticate_application,
    rotate_application_secret,
)

# --- METRIC SERVICE ---
from app.services.metric import (
    create_metric,
    get_metrics,
    get_metric_by_id,
    get_metrics_by_application,
    update_metric_by_id,
    delete_metric,
    get_application_performance_summary,
    get_slowest_endpoints,
)

# --- ALERT SERVICE ---
from app.services.alert import (
    create_alert_rule,
    get_alert_rules,
    get_alert_rule_by_id,
    get_alert_rules_by_application,
    update_alert_rule_by_id,
    delete_alert_rule,
    evaluate_alert_rules_for_application,
    create_alert_log,
    get_alert_logs,
    get_alert_log_by_id,
    get_alert_logs_by_application,
    process_and_dispatch_alerts,
)