from rest_framework import serializers
from .models import Education, WorkExperience, PortfolioItem
from django.utils import timezone

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'
        read_only_fields = ['employee', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate the education data.
        """
        if data.get('is_ongoing') and data.get('end_date'):
            raise serializers.ValidationError("Ongoing education cannot have an end date.")
        
        if not data.get('is_ongoing') and not data.get('end_date'):
            raise serializers.ValidationError("Non-ongoing education must have an end date.")

        if data.get('end_date') and data.get('start_date') and data['end_date'] < data['start_date']:
            raise serializers.ValidationError("End date cannot be before start date.")

        if data.get('start_date') and data['start_date'] > timezone.now().date():
            raise serializers.ValidationError("Start date cannot be in the future.")

        return data

    def create(self, validated_data):
        """
        Create and return a new Education instance.
        """
        validated_data['employee'] = self.context['request'].user.employee_profile
        return super().create(validated_data)

class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = '__all__'
        read_only_fields = ['employee', 'created_at', 'updated_at']

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
    view_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = PortfolioItem
        fields = '__all__'
        read_only_fields = ['employee', 'created_at', 'updated_at', 'view_count', 'like_count']

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