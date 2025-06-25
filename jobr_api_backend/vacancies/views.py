from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from accounts.models import ProfileOption
from common.pagination import NoLimitPagination
from .models import (
    Location, ContractType, Function, Language,
    Question, Skill, Vacancy, FunctionSkill,
    SalaryBenefit, Sector, ApplyVacancy, FavoriteVacancy, LikedVacancy,
    ApplicationStatus, JobListingPrompt, ProfileInterest,
    ExperienceCompany, ExperienceSchool,
)
from .serializers import (
    LocationSerializer, ContractTypeSerializer,
    FunctionSerializer, LanguageSerializer,
    QuestionSerializer, SkillSerializer,
    VacancySerializer, FunctionSkillSerializer,
    SalaryBenefitSerializer, SectorSerializer,
    ApplySerializer, FavoriteVacancySerializer, LikedVacancySerializer,
    JobListingPromptSerializer, ProfileInterestSerializer,
    ExperienceCompanySerializer, ExperienceSchoolSerializer
)

class SectorViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing sectors."""
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing locations."""
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

class ContractTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing contract types."""
    queryset = ContractType.objects.all()
    serializer_class = ContractTypeSerializer
    permission_classes = [IsAuthenticated]
class FunctionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing functions."""
    serializer_class = FunctionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NoLimitPagination  # Use custom pagination that returns all items

    def get_queryset(self):
        user = self.request.user
        
        # If user is not an employer, return all functions
        if not hasattr(user, 'selected_company'):
            return Function.objects.all()

        # Get selected company's sector
        company = user.selected_company
        if not company or not company.sector:
            return Function.objects.all()

        # Return functions for the company's sector
        return Function.objects.filter(sectors=company.sector)
    permission_classes = [IsAuthenticated]

class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing languages."""
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated]

class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing questions."""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

class InterestsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing questions."""
    queryset = ProfileInterest.objects.all()
    serializer_class = ProfileInterestSerializer
    permission_classes = [IsAuthenticated]

class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing skills."""
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """
        Get skills, optionally filtered by function.
        Returns skills ordered by weight within the function if specified.
        Returns empty queryset for nonexistent functions.
        """
        queryset = Skill.objects.all()
        function_id = self.request.query_params.get('function', None)

        if function_id:
            try:
                function_id = int(function_id)
            except (TypeError, ValueError):
                return Skill.objects.none()

            try:
                function = Function.objects.get(id=function_id)
                skill_ids = FunctionSkill.objects.filter(
                    function=function
                ).order_by('-weight').values_list('skill_id', flat=True)
                
                if not skill_ids:
                    return Skill.objects.none()
                
                # Preserve the ordering from skill_ids
                from django.db.models import Case, When
                preserved_order = Case(
                    *[When(id=id, then=pos) for pos, id in enumerate(skill_ids)]
                )
                queryset = queryset.filter(
                    id__in=skill_ids
                ).order_by(preserved_order)
            except Function.DoesNotExist:
                return Skill.objects.none()

        return queryset.distinct()

class SalaryBenefitViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing salary benefits."""
    queryset = SalaryBenefit.objects.all().order_by('id')
    serializer_class = SalaryBenefitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

class VacancyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing vacancies."""
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter vacancies based on user role."""
        user = self.request.user
        if user.role == ProfileOption.EMPLOYER:
            return Vacancy.objects.filter(company=user.selected_company)
        return Vacancy.objects.all()

    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests for vacancy updates."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        """Update a vacancy with proper permission checks."""
        user = self.request.user
        vacancy = self.get_object()

        # Check if user has permission to update this vacancy
        if user.role != ProfileOption.EMPLOYER:
            raise PermissionDenied("Only employers can update vacancies")
        
        if vacancy.company not in user.companies.all():
            raise PermissionDenied("You can only update vacancies for your companies")

        if not user.selected_company:
            raise ValidationError("Please select a company before updating a vacancy")
        
        if vacancy.company != user.selected_company:
            raise ValidationError("You can only update vacancies for your selected company")

        serializer.save()

    def perform_create(self, serializer):
        """Set company when creating a vacancy."""
        user = self.request.user
        if user.role != ProfileOption.EMPLOYER:
            raise PermissionDenied("Only employers can create vacancies")
        if not user.selected_company:
            raise ValidationError("Please select a company before creating a vacancy")
        serializer.save(company=user.selected_company, created_by=user)

class JobListingPromptViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing job listing prompts."""
    queryset = JobListingPrompt.objects.all().order_by('weight')
    serializer_class = JobListingPromptSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

class VacancyFilterView(generics.ListAPIView):
    """View for filtering and sorting vacancies."""
    serializer_class = VacancySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter and sort vacancies based on query parameters."""
        queryset = Vacancy.objects.all()

        # Filter by date
        date = self.request.query_params.get('date', None)
        if date:
            queryset = queryset.filter(date_times__date=date)

        # Filter by time range
        start_time = self.request.query_params.get('start_time', None)
        end_time = self.request.query_params.get('end_time', None)
        if start_time and end_time:
            queryset = queryset.filter(
                date_times__start_time__lte=end_time,
                date_times__end_time__gte=start_time
            )

        # Filter by sector
        sector = self.request.query_params.get('sector', None)
        if sector:
            queryset = queryset.filter(function__sectors__id=sector)

        # Filter by contract type
        contract_type = self.request.query_params.get('contract_type', None)
        if contract_type:
            queryset = queryset.filter(contract_type__id=contract_type)

        # Filter by skills

        skills_str = self.request.query_params.get('skills')
        if skills_str:
            skills = [skill.strip() for skill in skills_str.split(',') if skill.strip()]
            queryset = queryset.filter(skill__id__in=skills)

        language_str = self.request.query_params.get('languages')
        if language_str:
            languages = [language.strip() for language in language_str.split(',') if language.strip()]
            queryset = queryset.filter(languages__language__id__in=languages)

        # Filter by function
        function = self.request.query_params.get('function', None)
        if function:
            queryset = queryset.filter(function_id=function)

        # Filter by salary range
        min_salary = self.request.query_params.get('min_salary', None)
        max_salary = self.request.query_params.get('max_salary', None)
        if min_salary:
            queryset = queryset.filter(salary__gte=float(min_salary))
        if max_salary:
            queryset = queryset.filter(salary__lte=float(max_salary))

        # Filter by distance if user has location
        # if hasattr(self.request.user, 'employee_profile'):
        #     employee = self.request.user.employee_profile
        #     # Get employee's location from their address
        #     address = employee.address if hasattr(employee, 'address') else None
        #     if address and address.latitude and address.longitude:
        #         max_distance = float(self.request.query_params.get('max_distance', 50))  # Default 50km
        #         queryset = queryset.filter(
        #             company__address__latitude__isnull=False,
        #             company__address__longitude__isnull=False
        #         ).extra(
        #             where=[
        #                 """
        #                 ST_Distance_Sphere(
        #                     point(company_address.longitude, company_address.latitude),
        #                     point(%s, %s)
        #                 ) <= %s * 1000
        #                 """
        #             ],
        #             params=[address.longitude, address.latitude, max_distance]
        #         )

        # Sort by salary
        sort_by_salary = self.request.query_params.get('sort_by_salary', None)
        if sort_by_salary:
            if sort_by_salary.lower() == 'desc':
                queryset = queryset.order_by('-salary')
            else:
                queryset = queryset.order_by('salary')

        return queryset.distinct()

class ExperienceCompanyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ExperienceCompanySerializer
    permission_classes = [IsAuthenticated]
    queryset = ExperienceCompany.objects.all()

class ExperienceSchoolViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ExperienceSchoolSerializer
    permission_classes = [IsAuthenticated]
    queryset = ExperienceSchool.objects.all()

class FunctionSkillViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing function-skill relationships."""
    serializer_class = FunctionSkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get function-skill relationships, optionally filtered by function."""
        queryset = FunctionSkill.objects.all()
        function_id = self.request.query_params.get('function', None)
        
        if function_id:
            queryset = queryset.filter(function_id=function_id)
        
        return queryset.order_by('-weight')

class JobApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing job applications."""
    serializer_class = ApplySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter applications based on user role."""
        user = self.request.user
        if user.role == ProfileOption.EMPLOYER:
            return ApplyVacancy.objects.filter(vacancy__company__in=user.companies.all())
        elif user.role == ProfileOption.EMPLOYEE and hasattr(user, 'employee_profile'):
            return ApplyVacancy.objects.filter(employee=user.employee_profile)
        return ApplyVacancy.objects.none()

    def perform_create(self, serializer):
        """Create a job application."""
        user = self.request.user
        if user.role != ProfileOption.EMPLOYEE:
            raise PermissionDenied("Only employees can apply for jobs")
        if not hasattr(user, 'employee_profile'):
            raise ValidationError("Employee profile not found")
        serializer.save(employee=user.employee_profile)

    def update(self, request, *args, **kwargs):
        """Update application status."""
        instance = self.get_object()
        user = request.user

        # Only employers can update application status
        if user.role != ProfileOption.EMPLOYER:
            raise PermissionDenied("Only employers can update application status")

        # Ensure employer owns the vacancy
        if instance.vacancy.company not in user.companies.all():
            raise PermissionDenied("You can only update applications for your vacancies")

        # Update status
        new_status = request.data.get('status')
        if new_status not in dict(ApplicationStatus.choices):
            raise ValidationError("Invalid status")

        instance.status = new_status
        instance.notes = request.data.get('notes', instance.notes)
        instance.save()

        return Response(self.get_serializer(instance).data)

class FavoriteVacancyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing favorite vacancies."""
    serializer_class = FavoriteVacancySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get user's favorite vacancies."""
        user = self.request.user
        if user.role == ProfileOption.EMPLOYEE and hasattr(user, 'employee_profile'):
            return FavoriteVacancy.objects.filter(employee=user.employee_profile)
        return FavoriteVacancy.objects.none()

    def perform_create(self, serializer):
        """Add a vacancy to favorites."""
        user = self.request.user
        if user.role != ProfileOption.EMPLOYEE:
            raise PermissionDenied("Only employees can favorite vacancies")
        if not hasattr(user, 'employee_profile'):
            raise ValidationError("Employee profile not found")
        serializer.save(employee=user.employee_profile)

    def destroy(self, request, *args, **kwargs):
        """Remove a vacancy from favorites."""
        instance = self.get_object()
        if instance.employee.user != request.user:
            raise PermissionDenied("You can only remove your own favorites")
        return super().destroy(request, *args, **kwargs)

class CompanyVacanciesView(generics.ListAPIView):
    """View for listing all vacancies of a specific company."""
    serializer_class = VacancySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get all vacancies for the specified company."""
        company_id = self.kwargs.get('company_id')
        return Vacancy.objects.filter(company_id=company_id)

class AIVacancySuggestionsView(generics.ListAPIView):
    """View for AI-powered vacancy suggestions."""
    serializer_class = VacancySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get AI-suggested vacancies for the employee."""
        user = self.request.user
        if user.role != ProfileOption.EMPLOYEE or not hasattr(user, 'employee_profile'):
            return Vacancy.objects.none()

        # Base query for active vacancies
        queryset = Vacancy.objects.all()

        return queryset[:10]  # Return top 10 matches

class LikedVacancyView(generics.GenericAPIView):
    """Handle liked vacancy operations."""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get liked vacancies for the current employee."""
        if request.user.role != ProfileOption.EMPLOYEE or not hasattr(request.user, 'employee_profile'):
            return Response([])
        
        # Get the vacancies that the employee has liked
        liked_vacancies = Vacancy.objects.filter(
            liked_by_employees__employee=request.user.employee_profile
        )
        return Response(VacancySerializer(liked_vacancies, many=True, context={'request': request}).data)

    def post(self, request, *args, **kwargs):
        """Toggle like status for a vacancy."""
        if request.user.role != ProfileOption.EMPLOYEE:
            raise ValidationError("Only employees can like vacancies")
        
        if not hasattr(request.user, 'employee_profile'):
            raise ValidationError("Employee profile not found")
        
        # Get vacancy_id from URL kwargs
        vacancy_id = self.kwargs.get('vacancy_id')
        if not vacancy_id:
            raise ValidationError("Vacancy ID is required")
            
        # Get the vacancy instance
        from django.shortcuts import get_object_or_404
        vacancy = get_object_or_404(Vacancy, id=vacancy_id)
        
        # Check if the like already exists
        existing_like = LikedVacancy.objects.filter(
            employee=request.user.employee_profile,
            vacancy=vacancy
        ).first()
        
        if existing_like:
            # Unlike if already liked
            existing_like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        # Like if not already liked
        LikedVacancy.objects.create(
            employee=request.user.employee_profile,
            liked_by=request.user,
            vacancy=vacancy
        )
        
        # Return the updated vacancy data
        return Response(VacancySerializer(vacancy, context={'request': request}).data, status=status.HTTP_201_CREATED)