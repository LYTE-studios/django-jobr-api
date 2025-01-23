from django.db import models


class Location(models.Model):
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.location


class ContractType(models.Model):
    contract_type = models.CharField(max_length=255)

    def __str__(self):
        return self.contract_type


class Function(models.Model):
    function = models.CharField(max_length=255)

    def __str__(self):
        return self.function


class Question(models.Model):
    question = models.CharField(max_length=255)

    def __str__(self):
        return self.question


class Language(models.Model):
    language = models.CharField(max_length=255)

    def __str__(self):
        return self.language


class Skill(models.Model):
    skill = models.CharField(max_length=255)
    category = models.CharField(max_length=10, choices=[('hard', 'Hard'), ('soft', 'Soft')], default='hard')

    def __str__(self):
        return self.skill


class Extra(models.Model):
    extra = models.CharField(max_length=255)

    def __str__(self):
        return self.extra