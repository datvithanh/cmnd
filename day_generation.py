import datetime

dates = [(datetime.date.today() - datetime.timedelta(days=x)).strftime('%d-%m-%Y') for x in range(3650, 25185)][::-1]
with open('dates.txt', 'w+') as f:
    for date in dates:
        f.write(date + ',')