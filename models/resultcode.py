import enum


class ResultCode(enum.Enum):
    API_ERROR_AUTHENTICATION_FAILED = "api_error_authentication_failed"
    API_ERROR_NO_AUTHORIZATION = "api_error_no_authorization"
    API_ERROR_REQUIRED_FIELD_MISSING = "api_error_required_field_missing"
    ERROR_BANNED = "error_banned"
    ERROR_NO_AMP = "error_no_amp"
    ERROR_NO_CANONICALS = "error_no_canonicals"
    ERROR_OTHER = "error_other"
    ERROR_PROBLEMATIC_DOMAIN = "error_problematic_domain"
    ERROR_REPLY_FAILED = "error_reply_failed"
    ERROR_UNKNOWN = "error_unknown"
    ERROR_USER_OPTED_OUT = "error_user_opted_out"
    MEETS_CRITERIA = "meets_criteria"
    SUCCESS = "success"
    TWITTER_ERROR_IS_RETWEET = "twitter_error_is_retweet"
    TWITTER_ERROR_IS_NOT_CACHED = "twitter_error_is_not_cached"
