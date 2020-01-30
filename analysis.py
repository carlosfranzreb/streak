import csv
import datetime as dt
import numpy as np
import time


class Analyse:
    def __init__(self, csv_name):
        self.csv = self.openFile(csv_name)

    def openFile(self, csv_name):
        with open(csv_name, newline='') as csv_file:
            reader = csv.reader(csv_file)
            first = True
            keys = []
            data = []
            for row in reader:
                if first:
                    keys = row
                    first = False
                else:
                    data.append({})
                    for i in range(len(row)):
                        data[-1][keys[i]] = row[i]
        return data

    def avgTimeToSolve(self):
        t = dt.timedelta()
        for i in self.csv:
            t += self.timestamp(i['lastStageChange']) - \
                    self.timestamp(i['created'])
        t /= len(self.csv)
        return [t.days, time.strftime("%H:%M:%S",
                time.gmtime(t.seconds))]

    def timestamp(self, str_date):
        t = time.strptime(str_date, "%Y-%m-%d %H:%M:%S")
        return dt.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min,
                           t.tm_sec)

    def creators(self):
        creators = {}
        for i in self.csv:
            if i['creator'] in creators.keys():
                creators[i['creator']] += 1
            else:
                creators[i['creator']] = 1
        return creators

    def assigned(self):
        assigned = {}
        for i in self.csv:
            if i['assignedTo'] in assigned.keys():
                assigned[i['assignedTo']] += 1
            else:
                assigned[i['assignedTo']] = 1
        return assigned


if __name__ == "__main__":
    a = Analyse('SupportTickets_Resolved.csv')
    print(a.avgTimeToSolve())
    print(a.creators())
    print(a.assigned())
