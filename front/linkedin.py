from datetime import datetime
from front.models import Person, Education, LinkedinCompany, Position


# possible linkedin actions
ACTION_IMPORT = 'a_import'
ACTION_DELETE = 'a_delete'
ACTION_UPDATE = 'a_update'


def delete(profile):
    try:
        person = Person.objects.get(linkedin_id=profile.get('id'))
        person.deleted = datetime.now()
        person.save()
        return True
    except:
        return False


def save(profile, token):
    """
    Save a Linkedin profile to our database structure
    """

    ####
    # create the person
    ####

    # check if the person exists and delete CASCADE it if it already does

    try:
        person = Person.default.get(linkedin_id=profile.get('id')) # need to get either deleted or not
        person.delete()
    except:
        pass

    # import the person record

    person = Person(
        linkedin_id=profile.get('id'),
        first_name=profile.get('firstName'),
        last_name=profile.get('lastName'),
        email=profile.get('emailAddress'),
        headline=profile.get('headline'),
        num_connections=profile.get('numConnections'),
        num_connections_capped=profile.get('numConnectionsCapped'),
        num_recommenders=profile.get('numRecommenders'),
        picture_url=profile.get('pictureUrl'),
        interests=profile.get('interests'),
        summary=profile.get('summary'),
        profile_url=profile.get('publicProfileUrl'),
        specialties=profile.get('specialties'),
        location=profile.get('location', {}).get('name'),
        linkedin_authorization_code=token[0],
        linkedin_expires_in=token[1],
        linkedin_last_authorization_date=datetime.now())

    if profile.get('languages', {}).get('values'):
        person.languages = ", ".join(
            [lang.get('language', {}).get('name') for lang in profile.get('languages', {}).get('values')])

    if profile.get('skills', {}).get('values'):
        person.skills = ", ".join(
            [skill.get('skill', {}).get('name') for skill in profile.get('skills', {}).get('values')])

    person.save()

    ####
    # create the person's education records
    ####

    educations = profile.get('educations', {}).get('values', [])

    for item in educations:
        try:
            Education.objects.create(
                person=person,
                linkedin_id=item.get('id'),
                school_name=item.get('schoolName'),
                activities=item.get('activities'),
                degree=item.get('degree'),
                field_of_study=item.get('fieldOfStudy'),
                start_date=item.get('startDate', {}).get('year'),
                end_date=item.get('endDate', {}).get('year'))
        except:
            pass


    ####
    # create the person's positions
    ####

    positions = profile.get('positions', {}).get('values', [])

    for item in positions:
        # find or create the company
        try:
            if item.get('company', {}).get('id', None):
                # try to find by linkedin_id (will raise DoesNotExist if not found)
                company = LinkedinCompany.objects.get(linkedin_id=item.get('company').get('id'))
            else:
                # try to find by name (will raise DoesNotExist if not found)
                company = LinkedinCompany.objects.get(name__iexact=item.get('company').get('name'))
        except:
            company = LinkedinCompany.objects.create(
                linkedin_id=item.get('company', {}).get('id'),
                industry=item.get('company', {}).get('industry'),
                name=item.get('company', {}).get('name'),
                size=item.get('company', {}).get('size'))

        # create the position
        try:
            Position.objects.create(
                person=person,
                company=company,
                linkedin_id=item.get('id'),
                is_current=item.get('isCurrent'),
                start_date_month=item.get('startDate', {}).get('month'),
                start_date_year=item.get('startDate', {}).get('year'),
                end_date_month=item.get('endDate', {}).get('month'),
                end_date_year=item.get('endDate', {}).get('year'),
                summary=item.get('summary'),
                title=item.get('title'))
        except:
            pass


    ####
    # import is done, return the created person
    ####

    return person