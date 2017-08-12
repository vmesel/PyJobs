from datetime import date, timedelta
from freela.models import Freelancer, Freela

def send_seven_days_email():
    date_last_week = date.today() - timedelta(weeks=1)
    freelancers = Freelancer.objects.filter(data_inscrito__gt=date_last_week)
    print(freelancers)

send_seven_days_email()
