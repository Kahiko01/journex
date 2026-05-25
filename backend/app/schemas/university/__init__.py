"""
University Schemas Package
"""

# Import all schemas directly to avoid circular imports
from .course import CourseBase, CourseCreate, CourseUpdate, CourseResponse
from .cohort import (
    CohortBase, CohortCreate, CohortUpdate, CohortResponse,
    CohortDetailResponse, CohortMemberResponse, CohortJoinRequest,
    UserProgressResponse, UserProgressUpdate, LeaderboardEntry,
    CohortLeaderboardResponse, CohortStatisticsResponse
)
from .certification import CertificationBase, CertificationCreate, CertificationResponse, CertificateVerifyRequest

__all__ = [
    # Course
    "CourseBase", "CourseCreate", "CourseUpdate", "CourseResponse",
    # Cohort
    "CohortBase", "CohortCreate", "CohortUpdate", "CohortResponse",
    "CohortDetailResponse", "CohortMemberResponse", "CohortJoinRequest",
    "UserProgressResponse", "UserProgressUpdate", "LeaderboardEntry",
    "CohortLeaderboardResponse", "CohortStatisticsResponse",
    # Certification
    "CertificationBase", "CertificationCreate", "CertificationResponse", "CertificateVerifyRequest"
]
