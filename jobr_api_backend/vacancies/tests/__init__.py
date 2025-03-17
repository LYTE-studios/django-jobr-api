# Vacancies module tests
# This package contains comprehensive test suites for the vacancies module, including:
# - Models: Location, ContractType, Function, Question, Language, Skill, Vacancy, etc.
# - Serializers: VacancySerializer, ApplySerializer, etc.
# - Views: Vacancy creation, application, and management endpoints

from .test_serializers import *
from .test_views import *
from .test_base_models import *
from .test_vacancy_models import *