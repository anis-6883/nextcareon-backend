"""app/cache/keys.py - Redis cache key templates."""

CAREER_PATHS_LIST = "cache:career_paths:list"
CAREER_PATH_DETAIL = "cache:career_path:detail:{path_id}"
CAREER_PATH_MARKET_DATA = "cache:career_path:market:{path_id}"
JOB_OPENINGS = "cache:job_openings"
COMPANIES = "cache:companies"
ALUMNI_SHOWCASE = "cache:alumni_showcase"


def get_career_path_detail_key(path_id: str) -> str:
    return CAREER_PATH_DETAIL.format(path_id=path_id)
