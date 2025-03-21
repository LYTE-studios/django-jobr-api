# vacancies/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VacancyViewSet,
    ApplyViewSet,
    VacancyFilterView,
    ContractsTypesView,
    FunctionsView,
    LanguagesView,
    SkillsView,
    LocationsView,
    QuestionsView,
    ApplyForJobView,
    ProfileInterestsView,
    SalaryBenefitsView,
    VacancyApplicantsView
)

router = DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path(
        "locations/",
        LocationsView.as_view(),
        name="locations",
    ),
    path("apply/<int:vacancy_id>/", ApplyForJobView.as_view(), name="apply"),
    path("skills/", SkillsView.as_view(), name="skills"),
    path("languages/", LanguagesView.as_view(), name="languages"),
    path("functions/", FunctionsView.as_view(), name="functions"),
    path("contracts/", ContractsTypesView.as_view(), name="contracts"),
    path("questions/", QuestionsView.as_view(), name="questions"),
    path("profile-interests/", ProfileInterestsView.as_view(), name="profile-interests"),
    path("salary-benefits/", SalaryBenefitsView.as_view(), name="salary-benefits"),
    path("filter/", VacancyFilterView.as_view(), name="vacancy-filter"),
    path(
        "vacancies/<int:pk>/",
        VacancyViewSet.as_view({"get": "retrieve", "put": "update"}),
        name="vacancy-detail",
    ),
    path(
        "vacancies/",
        VacancyViewSet.as_view({"get": "list", "post": "create"}),
        name="vacancy-list",
    ),
    path(
        "vacancies/<int:vacancy_id>/applicants/",
        VacancyApplicantsView.as_view(),
        name="vacancy-applicants",
    ),
]
