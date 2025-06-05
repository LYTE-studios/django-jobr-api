from rest_framework import serializers
from .models import Education, WorkExperience, PortfolioItem
from django.utils import timezone

class EducationSerializer(serializers.ModelSerializer):
    """
    Serializer for Education model.
    """
    achievements = serializers.ListField(
        child=serializers.CharField(help_text="Individual achievement or accomplishment"),
        required=False,
        default=list,
        help_text="List of achievements during education"
    )

    class Meta:
        model = Education
        fields = '__all__'
        read_only_fields = ['employee', 'created_at', 'updated_at']
        swagger_schema_fields = {
            "title": "Education",
            "description": "Educational qualification details",
            "required": ["institution", "degree", "field_of_study", "description"]
        }

    def validate(self, data):
        """
        Validate the education data.
        """
        return data

    def create(self, validated_data):
        """
        Create and return a new Education instance.
        """
        validated_data['employee'] = self.context['request'].user.employee_profile
        return super().create(validated_data)

class WorkExperienceSerializer(serializers.ModelSerializer):
    """
    Serializer for WorkExperience model.
    """
    responsibilities = serializers.ListField(
        child=serializers.CharField(help_text="Individual job responsibility"),
        required=False,
        default=list,
        help_text="List of job responsibilities"
    )
    achievements = serializers.ListField(
        child=serializers.CharField(help_text="Individual achievement or accomplishment"),
        required=False,
        default=list,
        help_text="List of achievements in this position"
    )

    class Meta:
        model = WorkExperience
        fields = '__all__'
        read_only_fields = ['employee', 'created_at', 'updated_at']
        swagger_schema_fields = {
            "title": "Work Experience",
            "description": "Work experience details",
            "required": ["company_name", "position", "description", "start_date"]
        }

    def validate(self, data):
        """
        Validate the work experience data.
        """
        if data.get('is_current_position') and data.get('end_date'):
            raise serializers.ValidationError("Current position cannot have an end date.")
        
        if not data.get('is_current_position') and not data.get('end_date'):
            raise serializers.ValidationError("Past position must have an end date.")

        if data.get('end_date') and data.get('start_date') and data['end_date'] < data['start_date']:
            raise serializers.ValidationError("End date cannot be before start date.")

        if data.get('start_date') and data['start_date'] > timezone.now().date():
            raise serializers.ValidationError("Start date cannot be in the future.")

        return data

    def create(self, validated_data):
        """
        Create and return a new WorkExperience instance.
        """
        validated_data['employee'] = self.context['request'].user.employee_profile
        return super().create(validated_data)

class PortfolioItemSerializer(serializers.ModelSerializer):
    """
    Serializer for PortfolioItem model.
    """
    images = serializers.ListField(
        child=serializers.URLField(help_text="URL of an image"),
        required=False,
        default=list,
        help_text="List of image URLs for the portfolio item"
    )
    collaborators = serializers.ListField(
        child=serializers.CharField(help_text="Name of a collaborator"),
        required=False,
        default=list,
        help_text="List of collaborators who worked on this project"
    )
    tags = serializers.ListField(
        child=serializers.CharField(help_text="Individual tag or keyword"),
        required=False,
        default=list,
        help_text="List of tags describing the project"
    )
    view_count = serializers.IntegerField(
        read_only=True,
        help_text="Number of times this item has been viewed"
    )
    like_count = serializers.IntegerField(
        read_only=True,
        help_text="Number of likes this item has received"
    )

    class Meta:
        model = PortfolioItem
        fields = '__all__'
        read_only_fields = ['employee', 'created_at', 'updated_at', 'view_count', 'like_count']
        swagger_schema_fields = {
            "title": "Portfolio Item",
            "description": "Portfolio project or work sample",
            "required": ["title", "description", "date"]
        }

    def validate(self, data):
        """
        Validate the portfolio item data.
        """
        if data.get('date') and data['date'] > timezone.now().date():
            raise serializers.ValidationError("Date cannot be in the future.")

        if data.get('client_rating') and (data['client_rating'] < 0 or data['client_rating'] > 5):
            raise serializers.ValidationError("Client rating must be between 0 and 5.")

        if data.get('client_rating') and not data.get('client_name'):
            raise serializers.ValidationError("Client rating requires a client name.")

        if data.get('client_testimonial') and not data.get('client_name'):
            raise serializers.ValidationError("Client testimonial requires a client name.")

        return data

    def create(self, validated_data):
        """
        Create and return a new PortfolioItem instance.
        """
        validated_data['employee'] = self.context['request'].user.employee_profile
        return super().create(validated_data)