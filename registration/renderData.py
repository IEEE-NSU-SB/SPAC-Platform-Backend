
from registration.models import *


class Registration:

    def get_publish_status_phase01() -> bool:
        status = EventFormStatus_Phase01.objects.order_by('-updated_at').first()
        return bool(status and status.is_published)

    def get_publish_status_phase02() -> bool:
        status = EventFormStatus_Phase02.objects.order_by('-updated_at').first()
        return bool(status and status.is_published)

    def get_phase01_participant_count():
        return Form_Participant_Phase_1.objects.count()
    
    def get_phase02_participant_count():
        return Form_Participant_Phase_2.objects.count()
    
    def get_all_phase02_universities():
        return University.objects.all()
    
    def get_phase01_publish_status():
        return EventFormStatus_Phase01.objects.order_by('-updated_at').first()
    
    def get_phase02_publish_status():
        return EventFormStatus_Phase02.objects.order_by('-updated_at').first()
    
    def toggle_phase01_publish():
        """Toggle publish and return current status."""
        status = EventFormStatus_Phase01.objects.order_by('-updated_at').first()
        if not status:
            status = EventFormStatus_Phase01.objects.create(is_published=True)
        else:
            status.is_published = not status.is_published
            status.save(update_fields=['is_published'])

        return {'is_published': status.is_published}
    
    def toggle_phase02_publish():
        """Toggle publish and return current status."""
        status = EventFormStatus_Phase02.objects.order_by('-updated_at').first()
        if not status:
            status = EventFormStatus_Phase02.objects.create(is_published=True)
        else:
            status.is_published = not status.is_published
            status.save(update_fields=['is_published'])

        return {'is_published': status.is_published}